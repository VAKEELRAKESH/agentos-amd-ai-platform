from langchain_community.llms.fake import FakeListLLM
from langchain_community.llms.openai import OpenAI
from configs.settings import settings

def get_llm():
    if settings.DEBUG:
        responses = [
            "Final Answer: 1. Confirm the backend health endpoint. 2. Confirm the model endpoint. 3. Run a small agent task. 4. Verify memory storage.",
            "Final Answer: Research skipped for this debug test. The backend and model endpoint should be checked with local health calls.",
            "Final Answer: The AMD AI Platform backend test plan is: check /health, check /status/config, confirm vLLM responds, then run /agents/run.",
            "Final Answer: Quality score 9/10. The test workflow is sufficient for backend validation.\nPASS"
        ]
        # Pad with valid final answers so mock mode does not hit CrewAI iteration limits
        responses += ["Final Answer: Verified.\nPASS"] * 10
        return FakeListLLM(responses=responses)
    else:
        return OpenAI(
            model_name=settings.MODEL_NAME,
            openai_api_base=settings.MODEL_BASE_URL,
            openai_api_key="not-needed"
        )
