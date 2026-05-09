from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
sys.stdout.reconfigure(encoding='utf-8')

from configs.settings import settings
from backend.api import health_router, status_router, agents_router, tools_router, memory_router, route_router
from backend.models.memory import get_memory_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 {settings.APP_NAME} starting...")
    print(f"Version: {settings.APP_VERSION}")
    
    print("🧠 Initializing memory manager...")
    memory = get_memory_manager()
    stats = memory.get_stats()
    print(f"✅ Memory ready — {stats['total_memories']} memories loaded")
    
    yield
    print(f"🛑 {settings.APP_NAME} shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Agents + Fine-Tuning + Multimodal on AMD GPUs",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(status_router, prefix="/api/v1")
app.include_router(agents_router, prefix="/api/v1")
app.include_router(tools_router, prefix="/api/v1")
app.include_router(memory_router, prefix="/api/v1")
app.include_router(route_router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": "AMD AI Platform API",
        "docs": "/docs",
        "version": settings.APP_VERSION
    }
