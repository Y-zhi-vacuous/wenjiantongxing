import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import get_settings
from app.api import auth_router, essays_router, topics_router, classes_router, config_router, ability_router, students_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.db import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(essays_router, prefix="/api")
app.include_router(topics_router, prefix="/api")
app.include_router(classes_router, prefix="/api")
app.include_router(config_router, prefix="/api")
app.include_router(ability_router, prefix="/api")
app.include_router(students_router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


# 生产环境：托管前端静态文件
frontend_dir = settings.FRONTEND_DIR or os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
frontend_dir = os.path.abspath(frontend_dir)

if os.path.isdir(frontend_dir):
    # 先注册 SPA fallback，然后挂载静态文件
    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        file_path = os.path.join(frontend_dir, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dir, "index.html"))

    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dir, "assets")), name="assets")
