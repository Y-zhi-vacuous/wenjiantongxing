from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, func, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db import Base


class StudentAbility(Base):
    """学生写作能力画像 — 每次批改后更新"""
    __tablename__ = "student_abilities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False, index=True)

    # 综合评分
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)       # 加权均分
    essay_count: Mapped[int] = mapped_column(Integer, default=0)

    # 五维能力值 (0-100)
    thesis_ability: Mapped[float] = mapped_column(Float, default=0.0)      # 立意：审题/主题深度
    content_ability: Mapped[float] = mapped_column(Float, default=0.0)     # 内容：选材/细节/详略
    language_ability: Mapped[float] = mapped_column(Float, default=0.0)    # 语言：表达/修辞/文采
    structure_ability: Mapped[float] = mapped_column(Float, default=0.0)   # 结构：布局/过渡/呼应
    penmanship_ability: Mapped[float] = mapped_column(Float, default=0.0)  # 文面：卷面/标点/规范

    # 趋势数据 (JSON)
    score_history: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # [{essay_id, date, total_score, content, language, structure, penmanship}]

    # 优劣势分析
    strengths: Mapped[list | None] = mapped_column(JSON, nullable=True)
    weaknesses: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # 改进建议 (多条具体建议)
    improvement_plan: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # 最近一次批改的详细数据
    last_essay_id: Mapped[int | None] = mapped_column(ForeignKey("essays.id"), nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # 词语/修辞使用统计
    vocabulary_stats: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # {avg_word_count, common_typos:[], rhetorical_device_count:int}

    student = relationship("User")
