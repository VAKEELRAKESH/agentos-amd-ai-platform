from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from configs.settings import settings
from backend.workflows.task_workflow import run_task_workflow
from backend.services.response_guard import ensure_submission_ready_response
from typing import Optional

router = APIRouter(prefix="/agents", tags=["Agents"])

class TaskRequest(BaseModel):
    task: str = Field(..., min_length=10, max_length=1000,
                      description="The task for the AI agents to plan and execute",
                      example="Research the top 5 AI frameworks for building agents in 2024")

class TaskResponse(BaseModel):
    workflow_id: str
    task: str
    plan: str
    research: str = ""
    result: str
    validation: str = ""
    quality_verdict: str = ""
    duration_seconds: float
    status: str
    memory_id: str = ""
    recalled_context: list = []
    agents_used: list[str] = []
    route_decision: Optional[dict] = None

@router.post("/run", response_model=TaskResponse)
async def run_agent_task(request: TaskRequest):
    try:
        workflow_result = await run_task_workflow(request.task)
        workflow_result = ensure_submission_ready_response(workflow_result)
        return workflow_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info")
def agents_info():
    return {
        "available_agents": [
            "Strategic Planner",
            "Senior Research Analyst", 
            "Task Executor",
            "Quality Assurance Validator"
        ],
        "pipeline": "Planner → Researcher → Executor → Validator",
        "tools_per_agent": {
            "Strategic Planner": [],
            "Senior Research Analyst": ["web_search", "calculator"],
            "Task Executor": ["python_executor"],
            "Quality Assurance Validator": ["calculator"]
        },
        "mode": "debug (mock LLM)" if settings.DEBUG else "production (AMD vLLM)",
        "model": settings.MODEL_NAME,
        "endpoint": settings.MODEL_BASE_URL
    }
