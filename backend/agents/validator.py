from crewai import Agent
from ..tools import get_tools_by_name
from .base import get_llm

def create_validator_agent() -> Agent:
  return Agent(
    role="Quality Assurance Validator",
    goal=(
      "Review all agent outputs for accuracy, completeness, and clarity. "
      "Flag any gaps, contradictions, or unsupported claims. "
      "Produce a final validated summary with a quality score."
    ),
    backstory=(
      "You are a rigorous QA specialist who reviews AI-generated content. "
      "You check: Does the output address the original task? "
      "Are claims supported? Is anything missing? "
      "You always end with a structured verdict: "
      "PASS, PASS_WITH_NOTES, or NEEDS_REVISION."
    ),
    llm=get_llm(),
    tools=get_tools_by_name("calculator"),
    verbose=True,
    allow_delegation=False,
    max_iter=3
  )
