from sqlalchemy import String, Integer, Text, Enum as SAEnum, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum

from app.db import Base


class EssayStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    grading = "grading"
    graded = "graded"


class Essay(Base):
    __tablename__ = "essays"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("essay_topics.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(256), default="未命名作文")
    content: Mapped[str] = mapped_column(Text, default="")
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[EssayStatus] = mapped_column(SAEnum(EssayStatus), default=EssayStatus.draft)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    graded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    graded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    grading_requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    student = relationship("User", back_populates="essays", foreign_keys=[student_id])
    grader = relationship("User", foreign_keys=[graded_by])
    topic = relationship("EssayTopic", back_populates="essays")
    report = relationship("EssayReport", back_populates="essay", uselist=False)
