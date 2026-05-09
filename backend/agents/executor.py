from crewai import Agent
from .base import get_llm

def create_executor_agent() -> Agent:
    return Agent(
        role="Task Executor",
        goal="Execute assigned tasks thoroughly and return clear, structured results",
        backstory="""You are a precise executor who takes plans and implements them 
        step by step. You always validate your work before returning results and 
        flag any issues encountered during execution.""",
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )
