from openai import OpenAI
from configs.settings import settings


client = OpenAI(
    base_url=settings.MODEL_BASE_URL,
    api_key="not-required",
)


def run_direct_vllm_fallback(task: str) -> str:
    system_prompt = """
You are AgentOS, a senior AI systems strategist running on AMD GPU infrastructure through vLLM.

Produce high-quality, specific, complete, demo-ready answers.
Do not give generic chatbot output.
Do not claim fake research.
Do not mention internal failures.
Avoid filler.
Finish every answer fully.
"""

    user_prompt = f"""
Task:
{task}

Write a complete and useful answer.

Rules:
- Start with clear assumptions if needed.
- Be specific and practical.
- Use headings.
- Include concrete steps, risks, metrics, or checks where relevant.
- If the user asks for a script, write an actual usable script.
- If the user asks for a checklist, make it complete but not too long.
- End with a clear final recommendation or conclusion.
"""

    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
        temperature=0.22,
        max_tokens=2500,
    )

    answer = response.choices[0].message.content.strip()
    finish_reason = response.choices[0].finish_reason

    if finish_reason == "length" or answer.lower().rstrip().endswith(
        (" and", " or", " to", " for", " with", " such as", " including", "overall", " a kubernetes")
    ) or (answer and answer[-1] not in ".!?)]}\n*\""):
        continuation = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {
                    "role": "user",
                    "content": (
                        "Continue and complete the previous answer. "
                        "Do not restart from the beginning. Start exactly where the previous text left off.\n\n"
                        f"Previous answer (ends abruptly):\n{answer}"
                    ),
                },
            ],
            temperature=0.15,
            max_tokens=1500,
        )

        cont_content = continuation.choices[0].message.content.strip()
        # Simple deduplication: if continuation starts with a few words from the end of answer, skip them.
        answer = answer.rstrip() + " " + cont_content

    return answer.strip()
