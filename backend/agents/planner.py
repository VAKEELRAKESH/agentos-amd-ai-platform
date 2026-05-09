from crewai import Agent
from .base import get_llm

def create_planner_agent() -> Agent:
    return Agent(
        role="Strategic Planner",
        goal="Break down complex user tasks into clear, numbered, executable steps",
        backstory="""You are an expert project planner with 20 years of experience 
        decomposing complex problems. You always produce structured, numbered action 
        plans with clear outcomes for each step.""",
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )
