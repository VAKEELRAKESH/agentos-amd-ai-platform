from fastapi import APIRouter
from datetime import datetime, timezone
from configs.settings import settings

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/ready")
def health_ready():
    return {
        "ready": True,
        "checks": {
            "config": "ok",
            "vector_db_path": settings.VECTOR_DB_PATH
        }
    }

@router.get("/live")
def health_live():
    return {"alive": True}
