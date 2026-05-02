from pydantic import BaseModel
from datetime import datetime


class EssayCreate(BaseModel):
    topic_id: int
    title: str = "未命名作文"
    content: str = ""


class EssayResponse(BaseModel):
    id: int
    student_id: int
    topic_id: int
    title: str
    content: str
    word_count: int
    status: str
    submitted_at: datetime
    graded_at: datetime | None = None
    graded_by: int | None = None
    grading_requested_at: datetime | None = None

    model_config = {"from_attributes": True}


class BasicErrorsSchema(BaseModel):
    typos: list = []
    grammar: list = []
    punctuation: list = []


class ParagraphReviewSchema(BaseModel):
    paragraph_index: int
    original: str
    comment: str
    suggestion: str | None = None


class ReportResponse(BaseModel):
    id: int
    essay_id: int
    total_score: float
    score_thesis: float
    score_content: float
    score_language: float
    score_structure: float
    score_penmanship: float
    topic_match: str | None = None
    level: str | None = None
    deduction_reason: str | None = None
    word_count_actual: int | None = None
    basic_errors: dict | None = None
    paragraph_reviews: list | None = None
    overall_comment: str | None = None
    suggestions: list | None = None
    model_used: str | None = None
    processing_time_ms: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
