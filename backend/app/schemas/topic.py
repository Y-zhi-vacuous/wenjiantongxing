from pydantic import BaseModel
from datetime import datetime


class TopicCreate(BaseModel):
    title: str
    type: str = "命题"
    genre: str = "记叙文"
    difficulty: int = 3
    tips: str | None = None
    word_requirement: int = 600
    time_minutes: int = 45
    extra_requirements: str | None = None


class TopicResponse(BaseModel):
    id: int
    title: str
    type: str
    genre: str
    difficulty: int
    source: str
    creator_id: int | None = None
    tips: str | None = None
    word_requirement: int = 600
    time_minutes: int = 45
    extra_requirements: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
