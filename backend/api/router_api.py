from fastapi import APIRouter
from pydantic import BaseModel, Field
from ..workflows.router import get_router

router = APIRouter(prefix="/route", tags=["Router"])

class AnalyzeRequest(BaseModel):
    task: str = Field(..., min_length=5,
                      example="Calculate compound interest on $10000 at 7% for 10 years")

class AnalyzeResponse(BaseModel):
    task:           str
    task_type:      str
    confidence:     float
    pipeline:       list[str]
    tools_needed:   list[str]
    skip_research:  bool
    skip_validation:bool
    reason:         str
    estimated_steps:int
    pipeline_str:   str   # e.g. "Planner → Executor"

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_route(request: AnalyzeRequest):
    decision = get_router().route(request.task)
    return AnalyzeResponse(
        task=request.task,
        task_type=decision.task_type,
        confidence=decision.confidence,
        pipeline=decision.pipeline,
        tools_needed=decision.tools_needed,
        skip_research=decision.skip_research,
        skip_validation=decision.skip_validation,
        reason=decision.reason,
        estimated_steps=decision.estimated_steps,
        pipeline_str=" → ".join(decision.pipeline)
    )

@router.get("/types")
def get_route_types():
    return {
        "task_types": {
            "calculation": {
                "description": "Pure math/computation tasks",
                "pipeline": ["Task Executor"],
                "example": "Calculate the ROI of a $50k investment at 8% for 5 years"
            },
            "code": {
                "description": "Code writing, debugging, or explanation tasks",
                "pipeline": ["Strategic Planner", "Task Executor", "QA Validator"],
                "example": "Write a Python function to parse JSON logs"
            },
            "research": {
                "description": "Tasks requiring current web information",
                "pipeline": ["Strategic Planner", "Researcher", "Executor", "Validator"],
                "example": "Research the top open source LLMs available in 2024"
            },
            "analysis": {
                "description": "Reasoning and evaluation over given information",
                "pipeline": ["Strategic Planner", "Task Executor", "QA Validator"],
                "example": "Analyze the pros and cons of microservices architecture"
            },
            "general": {
                "description": "Mixed or unclear task type",
                "pipeline": ["Strategic Planner", "Task Executor", "QA Validator"],
                "example": "Help me plan my next project"
            }
        }
    }
