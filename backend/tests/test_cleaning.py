import asyncio
from backend.workflows.task_workflow import run_task_workflow


DIRTY_MARKERS = [
    "raw_output=",
    "exported_output=",
    "description=",
    "summary=",
    "maximum number of iterations",
    "Agent stopped due to iteration limit",
]


def get_field(result, name):
    if isinstance(result, dict):
        return result.get(name, "")
    return getattr(result, name, "")


async def test_workflow_cleaning():
    print("Starting mock workflow run...")

    result = await run_task_workflow(
        "Create a short validation checklist for backend response cleaning."
    )

    print("\n--- WORKFLOW RESULT ---")
    print("Workflow ID:", get_field(result, "workflow_id"))
    print("Status:", get_field(result, "status"))
    print("Verdict:", get_field(result, "quality_verdict"))
    print("Plan:", get_field(result, "plan"))
    print("Research:", get_field(result, "research"))
    print("Result:", get_field(result, "result"))
    print("Validation:", get_field(result, "validation"))

    assert get_field(result, "status") == "completed"
    assert get_field(result, "quality_verdict") in {
        "PASS",
        "PASS_WITH_NOTES",
        "NEEDS_REVISION",
    }

    for field in ["plan", "research", "result", "validation"]:
        value = str(get_field(result, field))
        for marker in DIRTY_MARKERS:
            assert marker not in value, f"Dirty marker leaked in {field}: {marker}"

    assert "Final result with some code" in str(get_field(result, "result"))
    assert "AUTO-VALIDATED" in str(get_field(result, "validation")) or get_field(result, "quality_verdict") == "PASS_WITH_NOTES"

    print("\ncleaning tests pass")


if __name__ == "__main__":
    asyncio.run(test_workflow_cleaning())
