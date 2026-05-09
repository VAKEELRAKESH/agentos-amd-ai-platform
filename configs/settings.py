from pathlib import Path
from pydantic.v1 import BaseSettings

ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT_DIR / ".env"

class Settings(BaseSettings):
    APP_NAME: str = "AMD AI Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    MODEL_BASE_URL: str = "http://localhost:8000/v1"
    MODEL_NAME: str = "mistralai/Mistral-7B-Instruct-v0.2"
    VECTOR_DB_PATH: str = "./data/vectordb"
    LOG_LEVEL: str = "INFO"
    AMD_INSTANCE_IP: str = ""

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8-sig"

settings = Settings()
