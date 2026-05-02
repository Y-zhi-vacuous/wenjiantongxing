"""v2.0 OCR 和评分配置 Schema"""
from pydantic import BaseModel


class OCRConfigUpdate(BaseModel):
    model_name: str = "glm-4.1v-thinking-flash"
    api_key: str = ""
    base_url: str | None = None


class OCRConfigResponse(BaseModel):
    id: int
    user_id: int
    model_name: str
    base_url: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class GradingConfigUpdate(BaseModel):
    provider: str = "zhipu"
    grading_model_name: str = "GLM-4-Flash-250414"
    ability_model_name: str | None = None
    api_key: str = ""
    base_url: str | None = None
    local_endpoint_url: str | None = None


class GradingConfigResponse(BaseModel):
    id: int
    user_id: int
    provider: str
    grading_model_name: str
    ability_model_name: str | None = None
    base_url: str | None = None
    local_endpoint_url: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


# 兼容旧版 AIConfig (deprecated)
from app.schemas.ai_config import AIConfigUpdate, AIConfigResponse
