from pydantic import BaseModel


class AIConfigUpdate(BaseModel):
    provider: str = "zhipu"
    model_name: str = "GLM-4-Flash-250414"
    grading_model_name: str = "GLM-4-Flash-250414"
    ocr_model_name: str = "glm-4.1v-thinking-flash"
    api_key: str = ""
    routing_strategy: str = "smart"


class AIConfigResponse(BaseModel):
    id: int
    user_id: int
    provider: str
    model_name: str
    grading_model_name: str | None = None
    ocr_model_name: str | None = None
    routing_strategy: str
    is_active: bool

    model_config = {"from_attributes": True}
