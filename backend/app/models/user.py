from sqlalchemy import String, Enum as SAEnum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum

from app.db import Base


class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), nullable=False)
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)
    grade: Mapped[str | None] = mapped_column(String(32))
    school: Mapped[str | None] = mapped_column(String(128))
    real_name: Mapped[str | None] = mapped_column(String(64))           # 教师实名
    teacher_cert: Mapped[str | None] = mapped_column(String(64))         # 教师资格证号
    default_password: Mapped[str | None] = mapped_column(String(256))    # 明文默认密码(仅教师创建学生时记录)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    essays = relationship("Essay", back_populates="student")
    ai_config = relationship("AIConfig", back_populates="user", uselist=False)
    ability = relationship("StudentAbility", back_populates="student", uselist=False)
