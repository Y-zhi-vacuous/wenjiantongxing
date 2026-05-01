from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, func, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db import Base


class EssayReport(Base):
    __tablename__ = "essay_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    essay_id: Mapped[int] = mapped_column(ForeignKey("essays.id"), unique=True, nullable=False)
    total_score: Mapped[float] = mapped_column(Float, default=0)
    score_thesis: Mapped[float] = mapped_column(Float, default=0)     # 立意 (满分10)
    score_content: Mapped[float] = mapped_column(Float, default=0)    # 内容 (满分15)
    score_language: Mapped[float] = mapped_column(Float, default=0)   # 语言 (满分10)
    score_structure: Mapped[float] = mapped_column(Float, default=0)  # 结构 (满分5)
    score_penmanship: Mapped[float] = mapped_column(Float, default=0) # 文面 (满分5)
    basic_errors: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    paragraph_reviews: Mapped[list | None] = mapped_column(JSON, nullable=True)
    overall_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggestions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    model_used: Mapped[str | None] = mapped_column(String(64), nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    essay = relationship("Essay", back_populates="report")
