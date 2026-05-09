from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from backend.tools import get_all_tools, get_tools_by_name

router = APIRouter(prefix="/tools", tags=["Tools"])

class ToolTestRequest(BaseModel):
    input: Dict[str, Any]

@router.get("/list")
def list_tools():
    tools = get_all_tools()
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.args_schema.model_json_schema() if tool.args_schema else {}
            }
            for tool in tools
        ],
        "count": len(tools)
    }

@router.post("/test/{tool_name}")
def test_tool(tool_name: str, request: ToolTestRequest):
    tools = {t.name: t for t in get_all_tools()}
    if tool_name not in tools:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found.")
    
    tool = tools[tool_name]
    try:
        # tool.run accepts keyword arguments or a dict depending on LangChain version
        # but the simplest way is often tool.invoke(request.input) or tool.run(**request.input)
        result = tool.run(request.input)
        return {
            "tool": tool_name,
            "input": request.input,
            "output": result,
            "success": True
        }
    except Exception as e:
        return {
            "tool": tool_name,
            "error": str(e),
            "success": False
        }
