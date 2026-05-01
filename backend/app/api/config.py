from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User, AIConfig, RoutingStrategy
from app.schemas import AIConfigUpdate, AIConfigResponse
from app.auth import get_current_user

router = APIRouter(prefix="/config", tags=["配置"])


@router.get("/ai", response_model=AIConfigResponse | None)
async def get_ai_config(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AIConfig).where(AIConfig.user_id == user.id))
    config = result.scalar_one_or_none()
    if not config:
        return None
    return AIConfigResponse.model_validate(config)


@router.put("/ai", response_model=AIConfigResponse)
async def update_ai_config(
    req: AIConfigUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AIConfig).where(AIConfig.user_id == user.id))
    config = result.scalar_one_or_none()
    if not config:
        config = AIConfig(user_id=user.id)
        db.add(config)
    config.provider = req.provider
    config.model_name = req.model_name
    config.grading_model_name = req.grading_model_name
    config.ocr_model_name = req.ocr_model_name
    config.routing_strategy = RoutingStrategy(req.routing_strategy)
    if req.api_key:
        config.api_key_encrypted = req.api_key
    await db.commit()
    await db.refresh(config)
    return AIConfigResponse.model_validate(config)


@router.post("/ai/test")
async def test_ai_connection(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.agents.router import test_connection
    result = await db.execute(select(AIConfig).where(AIConfig.user_id == user.id))
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=400, detail="请先配置 AI")
    ok = await test_connection(config)
    return {"success": ok, "message": "连接正常" if ok else "连接失败"}
