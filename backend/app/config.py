import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "文鉴同行"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production-use-a-real-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DATABASE_URL: str = "sqlite+aiosqlite:///./essay_app.db"

    REDIS_URL: str = "redis://localhost:6379/0"
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "essay-files"
    MINIO_SECURE: bool = False

    UPLOAD_DIR: str = "uploads"
    FRONTEND_DIR: str = ""
    CORS_ORIGINS: str = "http://localhost:5173"

    AI_PROVIDER: str = "zhipu"
    AI_MODEL: str = "glm-4-flash"
    AI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_database_url() -> str:
    """转换 DATABASE_URL 为 SQLAlchemy 可用的 async 格式"""
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        settings = get_settings()
        url = settings.DATABASE_URL

    print(f"[DB] Raw URL: {url[:50]}...")

    if url.startswith("postgresql://") and "+" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)

    print(f"[DB] Converted URL: {url[:60]}...")
    return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
