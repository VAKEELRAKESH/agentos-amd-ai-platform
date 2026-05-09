from crewai import Crew, Task, Process
from ..agents.planner import create_planner_agent
from ..agents.executor import create_executor_agent
from ..agents.researcher import create_researcher_agent
from ..agents.validator import create_validator_agent
from ..models.memory import get_memory_manager
from .router import get_router, RouteDecision, TaskType
from pydantic import BaseModel
from typing import Optional
from ..utils.output_cleaner import normalize_workflow_output
from configs.settings import settings
from backend.services.direct_vllm import run_direct_vllm_fallback
import time, uuid, os

class WorkflowResult(BaseModel):
    workflow_id: str
    task: str
    plan: str
    research: str
    result: str
    validation: str
    quality_verdict: str      # "PASS" | "PASS_WITH_NOTES" | "NEEDS_REVISION" | "UNKNOWN"
    duration_seconds: float
    status: str
    memory_id: str = ""
    recalled_context: list = []
    agents_used: list[str] = []
    route_decision: Optional[dict] = None   # serialized RouteDecision

# _extract_verdict moved to backend/utils/output_cleaner.py

async def run_task_workflow(user_task: str) -> WorkflowResult:
    start_time = time.time()
    workflow_id = str(uuid.uuid4())[:8]
    
    # â”€â”€ STEP 0: Route the task â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    router = get_router()
    route  = router.route(user_task)
    
    # Log routing decision
    print(f"\nROUTER: {route.task_type.value.upper()} | "
          f"Pipeline: {' â†’ '.join(route.pipeline)} | "
          f"Confidence: {route.confidence}")

    # â”€â”€ STEP 1: Recall relevant past work â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    memory = get_memory_manager()
    recalled = memory.recall_similar(user_task, n_results=2, min_similarity=0.25)
    
    context_str = ""
    if recalled:
        context_str = "\n\nRELEVANT PAST WORK (use to improve your plan):\n"
        for r in recalled:
            ts = r["metadata"].get("timestamp", "")[:10]
            sim = r["similarity"]
            snippet = r["snippet"][:250]
            context_str += f"  [{ts}] (sim={sim}) {snippet}\n"
    
    # â”€â”€ STEP 2: Create all four agents â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    planner    = create_planner_agent()
    researcher = create_researcher_agent()
    executor   = create_executor_agent()
    validator  = create_validator_agent()
    
    # â”€â”€ STEP 3: Define the 4-task pipeline â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    planning_task = Task(
        description=(
            f"Create a detailed, numbered step-by-step plan for:\n\n"
            f"{user_task}"
            f"{context_str}"
        ),
        agent=planner,
        expected_output=(
            "A numbered action plan (minimum 4 steps) with clear "
            "objectives for each step and expected outputs."
        )
    )

    research_task = Task(
        description=(
            f"Research the following task thoroughly:\n\n{user_task}\n\n"
            f"Use the web_search tool to find current, relevant information. "
            f"Follow the plan from the previous task. "
            f"Produce a structured research brief with:\n"
            f"  1. Key findings (bullet points)\n"
            f"  2. Relevant data or statistics\n"
            f"  3. Sources consulted\n"
            f"  4. Any gaps in available information"
        ),
        agent=researcher,
        expected_output=(
            "A structured research brief with key findings, "
            "data points, sources, and identified gaps."
        ),
        context=[planning_task]
    )

    execution_task = Task(
        description=(
            f"Execute the following task using the plan and research provided:\n\n"
            f"{user_task}\n\n"
            f"Build upon the plan and research from previous agents. "
            f"Produce a comprehensive, well-structured final output. "
            f"Use python_executor tool for any calculations or data processing needed."
        ),
        agent=executor,
        expected_output=(
            "A comprehensive, well-structured final output that fully "
            "addresses the original task with clear sections and conclusions."
        ),
        context=[planning_task, research_task]
    )

    validation_task = Task(
        description=(
            f"Review and validate all outputs for this task:\n\n"
            f"ORIGINAL TASK: {user_task}\n\n"
            f"Validate the execution output from the previous task. Check:\n"
            f"  1. Does the output fully address the original task? (Yes/No + reason)\n"
            f"  2. Are all claims supported or reasonable? (Yes/No + reason)\n"
            f"  3. Is anything critically missing? (List gaps if any)\n"
            f"  4. Overall quality score (1-10)\n\n"
            f"End your response with exactly one of these verdicts on its own line:\n"
            f"  PASS\n"
            f"  PASS_WITH_NOTES\n"
            f"  NEEDS_REVISION"
        ),
        agent=validator,
        expected_output=(
            "A structured validation report with checklist results, "
            "quality score, and a final verdict of PASS, "
            "PASS_WITH_NOTES, or NEEDS_REVISION."
        ),
        context=[planning_task, research_task, execution_task]
    )
    
    # â”€â”€ STEP 4: Assemble agents and tasks list â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    agents_list = []
    tasks_list  = []
    
    if route.task_type != TaskType.CALCULATION:
        agents_list.append(planner)
        tasks_list.append(planning_task)
    if not route.skip_research:
        agents_list.append(researcher)
        tasks_list.append(research_task)
    agents_list.append(executor)
    tasks_list.append(execution_task)
    if not route.skip_validation:
        agents_list.append(validator)
        tasks_list.append(validation_task)

    try:
        # If in DEBUG mode and MOCK_CREW is set, return mock 'dirty' data
        if settings.DEBUG and os.getenv("MOCK_CREW", "true") == "true":
            print("DEBUG MODE: Returning mock 'dirty' CrewAI output for cleaning validation.")
            duration = 1.5
            raw_results = {
                "plan": "1. Research\n2. Execute\ndescription='Task description' raw_output='Step 1: Done'",
                "research": "Found some data about AI. exported_output='Research summary here'",
                "result": "```markdown\nFinal result with some code\n```\nraw_output='The final answer'",
                "validation": "The output looks okay but I've reached the maximum number of iterations. PASS"
            }
        else:
            crew = Crew(
                agents=agents_list,
                tasks=tasks_list,
                process=Process.sequential,
                verbose=True
            )
            crew_output = crew.kickoff()
            
            # Extract individual task outputs
            task_outputs = crew_output.tasks_output if hasattr(crew_output, 'tasks_output') else []
            
            # Prepare raw data for cleaning
            raw_results = {}
            idx = 0
            if route.task_type != TaskType.CALCULATION:
                raw_results['plan'] = str(task_outputs[idx].raw) if len(task_outputs) > idx else str(planning_task.output or "")
                idx += 1
            else:
                raw_results['plan'] = "[Planning skipped by router - direct calculation]"

            if not route.skip_research:
                raw_results['research'] = str(task_outputs[idx].raw) if len(task_outputs) > idx else str(research_task.output or "")
                idx += 1
            else:
                raw_results['research'] = "[Research skipped by router]"
                
            raw_results['result'] = str(task_outputs[idx].raw) if len(task_outputs) > idx else str(execution_task.output or "")
            idx += 1
            
            if not route.skip_validation:
                raw_results['validation'] = str(task_outputs[idx].raw) if len(task_outputs) > idx else str(validation_task.output or "")
            else:
                raw_results['validation'] = "[Validation skipped by router]"
            
            duration = time.time() - start_time
            
        # â”€â”€ Clean and normalize â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        normalized = normalize_workflow_output(raw_results)
        plan_text = normalized['plan']
        research_text = normalized['research']
        exec_text = normalized['result']
        valid_text = normalized['validation']
        verdict = normalized.get('quality_verdict', "PASS" if route.skip_validation else "UNKNOWN")

        # â”€â”€ STEP 5: Store to memory â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        memory_id = ""
        try:
            memory_id = memory.store_workflow(
                workflow_id=workflow_id,
                task=user_task,
                plan=plan_text,
                result=exec_text,
                status="completed",
                duration=duration
            )
        except Exception as e:
            print(f"Memory storage failed: {e}")
        
        return WorkflowResult(
            workflow_id=workflow_id,
            task=user_task,
            plan=plan_text,
            research=research_text,
            result=exec_text,
            validation=valid_text,
            quality_verdict=verdict,
            duration_seconds=round(duration, 3),
            status="completed",
            memory_id=memory_id,
            recalled_context=recalled,
            agents_used=[a.role for a in agents_list],
            route_decision=route.model_dump()
        )
    
    except Exception as e:
        duration = time.time() - start_time
        return WorkflowResult(
            workflow_id=workflow_id,
            task=user_task,
            plan="", research="", result="",
            validation=f"Workflow failed: {str(e)}",
            quality_verdict="NEEDS_REVISION",
            duration_seconds=round(duration, 3),
            status="failed",
            agents_used=[],
            route_decision=route.model_dump()
        )

