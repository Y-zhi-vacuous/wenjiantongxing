from sqlalchemy import String, Integer, Enum as SAEnum, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum

from app.db import Base


class TopicType(str, enum.Enum):
    proposition = "命题"
    half_proposition = "半命题"
    material = "材料"
    topic = "话题"


class TopicGenre(str, enum.Enum):
    narrative = "记叙文"
    argumentative = "议论文"


class TopicSource(str, enum.Enum):
    system = "system"
    teacher = "teacher"


class EssayTopic(Base):
    __tablename__ = "essay_topics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    type: Mapped[TopicType] = mapped_column(SAEnum(TopicType), default=TopicType.proposition)
    genre: Mapped[TopicGenre] = mapped_column(SAEnum(TopicGenre), default=TopicGenre.narrative)
    difficulty: Mapped[int] = mapped_column(Integer, default=3)
    source: Mapped[TopicSource] = mapped_column(SAEnum(TopicSource), default=TopicSource.system)
    creator_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    tips: Mapped[str | None] = mapped_column(Text)
    word_requirement: Mapped[int] = mapped_column(Integer, default=600)      # 建议字数
    time_minutes: Mapped[int] = mapped_column(Integer, default=45)            # 建议用时(分钟)
    extra_requirements: Mapped[str | None] = mapped_column(Text)              # 附加写作要求
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    essays = relationship("Essay", back_populates="topic")
