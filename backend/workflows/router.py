from enum import Enum
from pydantic import BaseModel
from typing import Optional
import re

class TaskType(str, Enum):
    CALCULATION    = "calculation"    # Pure math/computation
    CODE           = "code"           # Write/debug/explain code
    RESEARCH       = "research"       # Needs web lookup
    ANALYSIS       = "analysis"       # Reason over given data
    GENERAL        = "general"        # Everything else

class RouteDecision(BaseModel):
    task_type:       TaskType
    confidence:      float            # 0.0 – 1.0
    pipeline:        list[str]        # Agent names in order
    tools_needed:    list[str]        # Tool names required
    skip_research:   bool             # True = no Researcher agent
    skip_validation: bool             # True = no Validator agent
    reason:          str              # Human-readable explanation
    estimated_steps: int              # Rough task complexity

class TaskRouter:
    """
    Keyword-based classifier.
    Fast, deterministic, zero LLM calls — keeps routing free.
    """

    CALCULATION_KEYWORDS = {
        "calculate", "compute", "math", "formula", "equation",
        "percentage", "average", "sum", "multiply", "divide",
        "square root", "integral", "derivative", "statistics",
        "mean", "median", "variance", "probability", "convert units"
    }

    CODE_KEYWORDS = {
        "write code", "python script", "javascript", "function",
        "algorithm", "debug", "refactor", "implement", "class",
        "api endpoint", "sql query", "regex", "parse", "script",
        "program", "code", "function", "method", "loop", "array"
    }

    RESEARCH_KEYWORDS = {
        "research", "find", "search", "what is", "who is",
        "latest", "current", "recent", "news", "compare",
        "best", "top", "recommend", "review", "trend",
        "state of", "overview", "explain", "difference between"
    }

    ANALYSIS_KEYWORDS = {
        "analyze", "analyse", "evaluate", "assess", "review",
        "pros and cons", "swot", "breakdown", "summarize",
        "critique", "identify", "list", "enumerate", "reason"
    }

    def _score_task(self, task_lower: str, keywords: set) -> float:
        """Return keyword hit rate as confidence score."""
        hits = sum(1 for kw in keywords if kw in task_lower)
        return min(hits / max(len(keywords) * 0.15, 1), 1.0)

    def _estimate_steps(self, task: str) -> int:
        """Rough complexity estimate from task length + conjunctions."""
        words = len(task.split())
        conjunctions = len(re.findall(
            r'\b(and|then|also|additionally|furthermore|next|finally)\b',
            task.lower()
        ))
        return min(max(2, words // 15 + conjunctions), 10)

    def route(self, task: str) -> RouteDecision:
        task_lower = task.lower().strip()

        scores = {
            TaskType.CALCULATION: self._score_task(task_lower, self.CALCULATION_KEYWORDS),
            TaskType.CODE:        self._score_task(task_lower, self.CODE_KEYWORDS),
            TaskType.RESEARCH:    self._score_task(task_lower, self.RESEARCH_KEYWORDS),
            TaskType.ANALYSIS:    self._score_task(task_lower, self.ANALYSIS_KEYWORDS),
        }

        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]

        # Fall back to GENERAL if no strong signal
        if best_score < 0.05:
            best_type  = TaskType.GENERAL
            best_score = 0.5

        steps = self._estimate_steps(task)

        # ── Routing rules ──────────────────────────────────────────
        if best_type == TaskType.CALCULATION:
            return RouteDecision(
                task_type       = TaskType.CALCULATION,
                confidence      = round(best_score, 2),
                pipeline        = ["Task Executor"],
                tools_needed    = ["calculator", "python_executor"],
                skip_research   = True,
                skip_validation = True,
                reason          = (
                    "Pure calculation detected. Routing directly to Executor "
                    "with math tools. No research or validation needed."
                ),
                estimated_steps = steps
            )

        elif best_type == TaskType.CODE:
            return RouteDecision(
                task_type       = TaskType.CODE,
                confidence      = round(best_score, 2),
                pipeline        = ["Strategic Planner", "Task Executor",
                                   "Quality Assurance Validator"],
                tools_needed    = ["python_executor", "calculator"],
                skip_research   = True,
                skip_validation = False,
                reason          = (
                    "Code generation task detected. Using Planner + Executor "
                    "+ Validator pipeline. Research skipped — code tasks need "
                    "logic, not web lookups."
                ),
                estimated_steps = steps
            )

        elif best_type == TaskType.RESEARCH:
            return RouteDecision(
                task_type       = TaskType.RESEARCH,
                confidence      = round(best_score, 2),
                pipeline        = ["Strategic Planner", "Senior Research Analyst",
                                   "Task Executor", "Quality Assurance Validator"],
                tools_needed    = ["web_search", "calculator"],
                skip_research   = False,
                skip_validation = False,
                reason          = (
                    "Research task detected. Full 4-agent pipeline activated. "
                    "Researcher will use web_search to gather current data."
                ),
                estimated_steps = steps
            )

        elif best_type == TaskType.ANALYSIS:
            return RouteDecision(
                task_type       = TaskType.ANALYSIS,
                confidence      = round(best_score, 2),
                pipeline        = ["Strategic Planner", "Task Executor",
                                   "Quality Assurance Validator"],
                tools_needed    = ["calculator", "python_executor"],
                skip_research   = True,
                skip_validation = False,
                reason          = (
                    "Analysis task detected. Planner + Executor + Validator "
                    "pipeline. Research skipped — analysis works on provided "
                    "context, not web data."
                ),
                estimated_steps = steps
            )

        else:  # GENERAL
            return RouteDecision(
                task_type       = TaskType.GENERAL,
                confidence      = round(best_score, 2),
                pipeline        = ["Strategic Planner", "Task Executor",
                                   "Quality Assurance Validator"],
                tools_needed    = ["web_search", "calculator"],
                skip_research   = True,
                skip_validation = False,
                reason          = (
                    "General task. Standard 3-agent pipeline. "
                    "Add more specific keywords to trigger specialized routing."
                ),
                estimated_steps = steps
            )

# Singleton
_router: Optional[TaskRouter] = None

def get_router() -> TaskRouter:
    global _router
    if _router is None:
        _router = TaskRouter()
    return _router
