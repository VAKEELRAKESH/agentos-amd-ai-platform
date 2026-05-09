from .search_tool import WebSearchTool
from .python_tool import PythonExecutorTool
from .calculator_tool import CalculatorTool

def get_all_tools():
    return [
        WebSearchTool(),
        PythonExecutorTool(),
        CalculatorTool()
    ]

def get_tools_by_name(*names: str):
    all_tools = {t.name: t for t in get_all_tools()}
    return [all_tools[n] for n in names if n in all_tools]
