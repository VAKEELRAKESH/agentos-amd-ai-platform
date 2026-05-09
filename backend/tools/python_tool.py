from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Set, ClassVar
from RestrictedPython import compile_restricted, safe_globals, PrintCollector
from RestrictedPython.Guards import safe_builtins, guarded_iter_unpack_sequence
import io, contextlib, traceback

class PythonInput(BaseModel):
    code: str = Field(..., description="Python code to execute. Must be safe, no file I/O or network calls.")

class PythonExecutorTool(BaseTool):
    name: str = "python_executor"
    description: str = """Executes safe Python code and returns the output.
    Use this for calculations, data transformations, sorting, 
    statistical analysis, or any logic requiring computation.
    Do NOT use for file operations or network requests."""
    args_schema: Type[BaseModel] = PythonInput

    BLOCKED_IMPORTS: ClassVar[Set[str]] = {"os", "sys", "subprocess", "socket", "requests", 
                        "urllib", "httpx", "pathlib", "shutil", "glob"}

    def _run(self, code: str) -> str:
        # Block dangerous imports
        for blocked in self.BLOCKED_IMPORTS:
            if f"import {blocked}" in code or f"from {blocked}" in code:
                return f"Error: Import of '{blocked}' is not allowed for security reasons."
        try:
            byte_code = compile_restricted(code, filename="<agent_code>", mode="exec")
            local_vars = {}
            restricted_globals = dict(safe_globals)
            restricted_globals["__builtins__"] = dict(safe_builtins)
            # Add common safe utilities
            safe_utils = {
                "sum": sum, "len": len, "sorted": sorted, 
                "min": min, "max": max, "enumerate": enumerate,
                "zip": zip, "reversed": reversed, "list": list,
                "dict": dict, "set": set, "tuple": tuple,
                "range": range, "abs": abs, "round": round,
                "int": int, "float": float, "str": str, "bool": bool
            }
            restricted_globals["__builtins__"].update(safe_utils)
            
            restricted_globals["__builtins__"]["_getiter_"] = iter
            restricted_globals["__builtins__"]["_getattr_"] = getattr
            restricted_globals["_getiter_"] = iter
            restricted_globals["_unpack_sequence_"] = guarded_iter_unpack_sequence
            
            class Collector:
                def __init__(self): self.txt = []
                def __call__(self, _getattr_=None): return self
                def write(self, text): self.txt.append(text)
                def _call_print(self, *args): self.txt.append(" ".join(map(str, args)) + "\n")
            
            collector = Collector()
            restricted_globals["_print_"] = collector
            
            exec(byte_code, restricted_globals, local_vars)
            
            output = "".join(collector.txt)
            if not output and local_vars:
                # Filter out internal/function variables
                results = {k: v for k, v in local_vars.items() if not k.startswith('__')}
                if results:
                    last_val = list(results.values())[-1]
                    output = str(last_val)
            return output if output else "Code executed successfully (no output)."
        except Exception as e:
            return f"Execution error: {traceback.format_exc(limit=2)}"

    async def _arun(self, code: str) -> str:
        return self._run(code)
