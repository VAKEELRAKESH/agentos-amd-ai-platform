from langchain.tools import BaseTool
from duckduckgo_search import DDGS
from pydantic import BaseModel, Field
from typing import Type
import json

class SearchInput(BaseModel):
    query: str = Field(..., description="The search query to look up")
    max_results: int = Field(default=3, description="Number of results to return")

class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = """Searches the web for current information. 
    Use this when you need facts, recent news, or information 
    you don't already know. Input should be a clear search query."""
    args_schema: Type[BaseModel] = SearchInput

    def _run(self, query: str, max_results: int = 3) -> str:
        backends = ["api", "html", "lite"]
        for backend in backends:
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=max_results, backend=backend))
                if results:
                    formatted = []
                    for i, r in enumerate(results, 1):
                        formatted.append(
                            f"[{i}] {r.get('title','No title')}\n"
                            f"    URL: {r.get('href','N/A')}\n"
                            f"    {r.get('body','No description')[:200]}..."
                        )
                    return "\n\n".join(formatted)
            except Exception:
                continue
        # Graceful fallback — agents continue working even if search is blocked
        return (f"[SEARCH UNAVAILABLE — Rate limited]\n"
                f"Query was: '{query}'\n"
                f"Tip: Results will work normally on AMD cloud deployment.")

    async def _arun(self, query: str, max_results: int = 3) -> str:
        return self._run(query, max_results)
