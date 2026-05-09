from fastapi import APIRouter
import platform
import psutil
from configs.settings import settings

router = APIRouter(prefix="/status", tags=["Status"])

@router.get("/system")
def status_system():
    mem = psutil.virtual_memory()
    return {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "cpu_count": psutil.cpu_count(logical=True),
        "memory_total_gb": round(mem.total / (1024**3), 2),
        "memory_available_gb": round(mem.available / (1024**3), 2),
        "gpu_available": False,
        "model_backend_url": settings.MODEL_BASE_URL
    }

@router.get("/config")
def status_config():
    config_dict = settings.model_dump() if hasattr(settings, "model_dump") else settings.dict()
    safe_config = {}
    for k, v in config_dict.items():
        k_upper = k.upper()
        if not any(sensitive in k_upper for sensitive in ["KEY", "SECRET", "PASSWORD", "TOKEN"]):
            safe_config[k] = v
    return safe_config
