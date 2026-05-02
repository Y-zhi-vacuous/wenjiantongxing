"""
配置 API — v2.0

角色分离:
  - 学生: OCR 配置 (GET/PUT /config/ocr)
  - 教师: 评分配置 (GET/PUT /config/grading)
  - 旧版 /config/ai 保留但标记 deprecated
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User, AIConfig, OCRConfig, GradingConfig, GradingProvider, RoutingStrategy
from app.schemas import AIConfigUpdate, AIConfigResponse
from app.schemas.ai_config_v2 import (
    OCRConfigUpdate, OCRConfigResponse,
    GradingConfigUpdate, GradingConfigResponse,
)
from app.auth import get_current_user

router = APIRouter(prefix="/config", tags=["配置"])


# ──────────────────────────────────────────────
# v2.0: OCR 配置（学生端）
# ──────────────────────────────────────────────

@router.get("/ocr", response_model=OCRConfigResponse | None)
async def get_ocr_config(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(OCRConfig).where(OCRConfig.user_id == user.id))
    config = result.scalar_one_or_none()
    if not config:
        return None
    return OCRConfigResponse.model_validate(config)


@router.put("/ocr", response_model=OCRConfigResponse)
async def update_ocr_config(
    req: OCRConfigUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(OCRConfig).where(OCRConfig.user_id == user.id))
    config = result.scalar_one_or_none()
    if not config:
        config = OCRConfig(user_id=user.id)
        db.add(config)
    config.model_name = req.model_name
    if req.api_key:
        config.api_key_encrypted = req.api_key
    if req.base_url is not None:
        config.base_url = req.base_url
    await db.commit()
    await db.refresh(config)
    return OCRConfigResponse.model_validate(config)


@router.post("/ocr/test")
async def test_ocr_connection(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.agents.router import test_connection
    result = await db.execute(select(OCRConfig).where(OCRConfig.user_id == user.id))
    config = result.scalar_one_or_none()
    if not config or not config.api_key_encrypted:
        raise HTTPException(status_code=400, detail="请先配置 OCR 模型")

    # OCR 测试使用 zhipu 协议
    ok = await test_connection(
        provider="zhipu",
        api_key=config.api_key_encrypted,
        model=config.model_name,
        base_url=config.base_url,
    )
    return {"success": ok, "message": "连接正常" if ok else "连接失败"}


# ──────────────────────────────────────────────
# v2.0: 评分配置（教师端）
# ──────────────────────────────────────────────

@router.get("/grading", response_model=GradingConfigResponse | None)
async def get_grading_config(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.role.value != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可配置评分模型")
    result = await db.execute(select(GradingConfig).where(GradingConfig.user_id == user.id))
    config = result.scalar_one_or_none()
    if not config:
        return None
    return GradingConfigResponse.model_validate(config)


@router.put("/grading", response_model=GradingConfigResponse)
async def update_grading_config(
    req: GradingConfigUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.role.value != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可配置评分模型")
    result = await db.execute(select(GradingConfig).where(GradingConfig.user_id == user.id))
    config = result.scalar_one_or_none()
    if not config:
        config = GradingConfig(user_id=user.id)
        db.add(config)
    config.provider = GradingProvider(req.provider) if req.provider in [p.value for p in GradingProvider] else GradingProvider.zhipu
    config.grading_model_name = req.grading_model_name
    config.ability_model_name = req.ability_model_name
    if req.api_key:
        config.api_key_encrypted = req.api_key
    if req.base_url is not None:
        config.base_url = req.base_url
    if req.local_endpoint_url is not None:
        config.local_endpoint_url = req.local_endpoint_url
    await db.commit()
    await db.refresh(config)
    return GradingConfigResponse.model_validate(config)


@router.post("/grading/test")
async def test_grading_connection(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.role.value != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可测试评分连接")
    from app.agents.router import test_connection
    result = await db.execute(select(GradingConfig).where(GradingConfig.user_id == user.id))
    config = result.scalar_one_or_none()
    if not config or not config.is_active:
        raise HTTPException(status_code=400, detail="请先配置评分模型")

    ok = await test_connection(
        provider=config.provider.value,
        api_key=config.api_key_encrypted or "",
        model=config.grading_model_name,
        base_url=config.base_url,
        local_endpoint_url=config.local_endpoint_url,
    )
    return {"success": ok, "message": "连接正常" if ok else "连接失败"}


# ──────────────────────────────────────────────
# 旧版兼容（deprecated）
# ──────────────────────────────────────────────

@router.get("/ai", response_model=AIConfigResponse | None, deprecated=True)
async def get_ai_config(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AIConfig).where(AIConfig.user_id == user.id))
    config = result.scalar_one_or_none()
    if not config:
        return None
    return AIConfigResponse.model_validate(config)


@router.put("/ai", response_model=AIConfigResponse, deprecated=True)
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


@router.post("/ai/test", deprecated=True)
async def test_ai_connection(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.agents.router import test_connection
    result = await db.execute(select(AIConfig).where(AIConfig.user_id == user.id))
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=400, detail="请先配置 AI")
    ok = await test_connection(
        provider=config.provider,
        api_key=config.api_key_encrypted or "",
        model=config.model_name,
    )
    return {"success": ok, "message": "连接正常" if ok else "连接失败"}
