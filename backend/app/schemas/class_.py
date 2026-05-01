from pydantic import BaseModel
from datetime import datetime


class ClassCreate(BaseModel):
    name: str


class ClassResponse(BaseModel):
    id: int
    name: str
    teacher_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AddStudentRequest(BaseModel):
    username: str
