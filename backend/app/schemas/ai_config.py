from pydantic import BaseModel


class AIConfigUpdate(BaseModel):
    provider: str = "claude"
    model_name: str = "claude-sonnet-4-6"
    api_key: str = ""
    routing_strategy: str = "smart"


class AIConfigResponse(BaseModel):
    id: int
    user_id: int
    provider: str
    model_name: str
    routing_strategy: str
    is_active: bool

    model_config = {"from_attributes": True}
