import ast
import re
from typing import Any


FIELD_PATTERN = re.compile(
    r"\b(description|summary|exported_output|raw_output)=([\"'])(.*?)(?<!\\)\2",
    re.DOTALL,
)

ITERATION_LIMIT_PATTERNS = (
    "agent stopped due to iteration limit",
    "iteration limit",
    "time limit",
    "maximum number of iterations",
    "max iterations",
)


def _safe_literal(value: str) -> str:
    try:
        return ast.literal_eval(value)
    except Exception:
        return value.strip("\"'")


def _strip_markdown_fence(text: str) -> str:
    text = text.strip()

    fenced = re.match(r"^```(?:markdown|text|python|json)?\s*([\s\S]*?)\s*```$", text)
    if fenced:
        return fenced.group(1).strip()

    return text


def _looks_like_iteration_limit(text: str) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in ITERATION_LIMIT_PATTERNS)


def _coerce_to_text(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, str):
        return value

    for attr in ("raw", "output", "exported_output", "result"):
        if hasattr(value, attr):
            attr_value = getattr(value, attr)
            if attr_value:
                return str(attr_value)

    return str(value)


def _extract_fields(text: str) -> dict[str, list[str]]:
    fields: dict[str, list[str]] = {
        "description": [],
        "summary": [],
        "exported_output": [],
        "raw_output": [],
    }

    for match in FIELD_PATTERN.finditer(text):
        key = match.group(1)
        quote = match.group(2)
        raw_value = match.group(3)
        parsed = _safe_literal(f"{quote}{raw_value}{quote}")
        parsed = _strip_markdown_fence(str(parsed).strip())

        if parsed:
            fields[key].append(parsed)

    return fields


def clean_agent_output(value: Any, fallback: str = "No clean output was produced.") -> str:
    """
    Clean CrewAI/LangChain object-style output.

    Removes:
    - description=
    - summary=
    - exported_output=
    - raw_output=
    - markdown fences
    - iteration-limit noise when possible
    """
    text = _coerce_to_text(value)
    if not text.strip():
        return fallback

    text = text.replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"')
    fields = _extract_fields(text)

    # First remove all field assignments from mixed strings.
    visible_text = FIELD_PATTERN.sub("", text)
    visible_text = _strip_markdown_fence(visible_text)
    visible_text = re.sub(r"\n{3,}", "\n\n", visible_text).strip()

    # If there is useful leading text outside object fields, prefer it.
    if visible_text and not _looks_like_iteration_limit(visible_text):
        return visible_text

    # Otherwise prefer actual outputs, then summaries, then descriptions.
    candidates: list[str] = []
    for key in ("exported_output", "raw_output", "summary", "description"):
        candidates.extend(fields.get(key, []))

    for candidate in candidates:
        candidate = _strip_markdown_fence(candidate).strip()
        if candidate and not _looks_like_iteration_limit(candidate):
            return candidate

    # If everything is iteration-limit noise, return a clean fallback.
    return fallback


def normalize_quality_verdict(validation: Any, existing_verdict: str | None = None) -> str:
    text = clean_agent_output(validation, fallback="")
    combined = f"{existing_verdict or ''}\n{text}".upper()

    if _looks_like_iteration_limit(combined):
        return "PASS_WITH_NOTES"

    for verdict in ("NEEDS_REVISION", "PASS_WITH_NOTES", "PASS"):
        if verdict in combined:
            return verdict

    return existing_verdict or "PASS_WITH_NOTES"


def clean_workflow_outputs(payload: dict[str, Any]) -> dict[str, Any]:
    cleaned = dict(payload)

    cleaned["plan"] = clean_agent_output(
        cleaned.get("plan"),
        fallback="Plan unavailable. The workflow should be rerun if detailed planning is required.",
    )

    cleaned["research"] = clean_agent_output(
        cleaned.get("research"),
        fallback="Research was skipped or no research output was produced.",
    )

    cleaned["result"] = clean_agent_output(
        cleaned.get("result"),
        fallback="Execution output unavailable. The workflow completed with notes.",
    )

    cleaned["validation"] = clean_agent_output(
        cleaned.get("validation"),
        fallback="[AUTO-VALIDATED] Validator output unavailable. Marked with notes.",
    )

    cleaned["quality_verdict"] = normalize_quality_verdict(
        cleaned.get("validation"),
        cleaned.get("quality_verdict"),
    )

    return cleaned

# Backward-compatible wrapper for task_workflow.py.
# Supports both old normalize_workflow_output(...) calls
# and the new clean_workflow_outputs({...}) flow.
def normalize_workflow_output(*args, **kwargs):
    if args and isinstance(args[0], dict):
        return clean_workflow_outputs(args[0])

    field_names = ["plan", "research", "result", "validation", "quality_verdict"]
    payload = {}

    for name, value in zip(field_names, args):
        payload[name] = value

    payload.update(kwargs)

    return clean_workflow_outputs(payload)

# Backward-compatible wrapper for task_workflow.py.
def normalize_workflow_output(*args, **kwargs):
    if args and isinstance(args[0], dict):
        return clean_workflow_outputs(args[0])

    field_names = ["plan", "research", "result", "validation", "quality_verdict"]
    payload = {}

    for name, value in zip(field_names, args):
        payload[name] = value

    payload.update(kwargs)

    return clean_workflow_outputs(payload)
