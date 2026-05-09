from crewai import Agent
from ..tools import get_tools_by_name
from .base import get_llm

def create_researcher_agent() -> Agent:
  return Agent(
    role="Senior Research Analyst",
    goal=(
      "Gather accurate, current information using available tools. "
      "Always cite sources. Never fabricate data. "
      "Produce a structured research brief with key findings."
    ),
    backstory=(
      "You are a meticulous research analyst with expertise in technology, "
      "AI, and data science. You use web search to verify facts and produce "
      "evidence-based research briefs. You clearly distinguish between "
      "verified facts and inferences."
    ),
    llm=get_llm(),
    tools=get_tools_by_name("web_search", "calculator"),
    verbose=True,
    allow_delegation=False,
    max_iter=4
  )
