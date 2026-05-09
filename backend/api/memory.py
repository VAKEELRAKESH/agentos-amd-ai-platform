from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ..models.memory import get_memory_manager

router = APIRouter(prefix="/memory", tags=["Memory"])

@router.get("/stats")
def get_memory_stats():
    try:
        return get_memory_manager().get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recall")
def recall_memory(query: str, n_results: int = 3, min_similarity: float = 0.3):
    try:
        results = get_memory_manager().recall_similar(query, n_results, min_similarity)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear")
def clear_memory():
    try:
        result = get_memory_manager().clear_all()
        return { "message": "Memory cleared", "details": result }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
