"""v2.0 OCR 和评分配置 Schema

评分模型与能力分析模型可分别配置不同的提供商、模型名称和 API Key。
"""
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
    # 评分模型
    grading_provider: str = "zhipu"
    grading_model_name: str = "GLM-4-Flash-250414"
    grading_api_key: str = ""
    grading_base_url: str | None = None
    grading_local_url: str | None = None
    # 能力分析模型
    ability_provider: str | None = None
    ability_model_name: str | None = None
    ability_api_key: str = ""
    ability_base_url: str | None = None
    ability_local_url: str | None = None


class GradingConfigResponse(BaseModel):
    id: int
    user_id: int
    # 评分模型
    grading_provider: str = "zhipu"
    grading_model_name: str = "GLM-4-Flash-250414"
    grading_base_url: str | None = None
    grading_local_url: str | None = None
    # 能力分析模型
    ability_provider: str | None = None
    ability_model_name: str | None = None
    ability_base_url: str | None = None
    ability_local_url: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


# 兼容旧版 AIConfig (deprecated)
from app.schemas.ai_config import AIConfigUpdate, AIConfigResponse
