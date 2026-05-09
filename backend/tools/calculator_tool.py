from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, ClassVar
import ast, math, operator

class CalculatorInput(BaseModel):
    expression: str = Field(..., description="Math expression to evaluate. E.g. '2 ** 10', 'sqrt(144)', '(15 * 8) / 3'")

class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = """Evaluates mathematical expressions safely.
    Supports: +, -, *, /, **, sqrt, log, sin, cos, tan, pi, e, abs, round.
    Use this for any numerical calculation needed during task execution."""
    args_schema: Type[BaseModel] = CalculatorInput

    SAFE_FUNCTIONS: ClassVar[Dict[str, Any]] = {
        "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "abs": abs, "round": round, "pi": math.pi, "e": math.e,
        "floor": math.floor, "ceil": math.ceil, "pow": math.pow
    }

    SAFE_OPERATORS: ClassVar[Dict[Any, Any]] = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.USub: operator.neg,
        ast.UAdd: operator.pos, ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv
    }

    def _safe_eval(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name) and node.id in self.SAFE_FUNCTIONS:
            return self.SAFE_FUNCTIONS[node.id]
        elif isinstance(node, ast.BinOp):
            op = self.SAFE_OPERATORS.get(type(node.op))
            if op:
                return op(self._safe_eval(node.left), self._safe_eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            op = self.SAFE_OPERATORS.get(type(node.op))
            if op:
                return op(self._safe_eval(node.operand))
        elif isinstance(node, ast.Call):
            func = self._safe_eval(node.func)
            if callable(func):
                args = [self._safe_eval(a) for a in node.args]
                return func(*args)
        raise ValueError(f"Unsafe expression: {ast.dump(node)}")

    def _run(self, expression: str) -> str:
        try:
            expression = expression.replace("^", "**")
            tree = ast.parse(expression, mode="eval")
            result = self._safe_eval(tree.body)
            return f"Result: {result}"
        except Exception as e:
            return f"Calculation error: {str(e)}"

    async def _arun(self, expression: str) -> str:
        return self._run(expression)
