from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "文鉴同行"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production-use-a-real-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    DATABASE_URL: str = "sqlite+aiosqlite:///./essay_app.db"

    REDIS_URL: str = "redis://localhost:6379/0"

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "essay-files"
    MINIO_SECURE: bool = False

    UPLOAD_DIR: str = "uploads"
    FRONTEND_DIR: str = ""

    AI_PROVIDER: str = "zhipu"
    AI_MODEL: str = "glm-4-flash"
    AI_API_KEY: str = ""

    class Config:
        env_file = ".env"


def get_database_url() -> str:
    """转换 DATABASE_URL 为 SQLAlchemy 可用的格式"""
    settings = get_settings()
    url = settings.DATABASE_URL
    # Render PostgreSQL: postgres://user:pass@host/db → postgresql+asyncpg://user:pass@host/db
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
