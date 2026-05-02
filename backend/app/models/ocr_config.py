"""
OCR 配置模型 — 学生端

v2.0: 从 AIConfig 拆分，仅包含 OCR 相关配置。
学生可配置 OCR 模型、API Key、自定义端点。
"""
from sqlalchemy import String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class OCRConfig(Base):
    __tablename__ = "ocr_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(64), default="glm-4.1v-thinking-flash")
    api_key_encrypted: Mapped[str | None] = mapped_column(String(512))
    base_url: Mapped[str | None] = mapped_column(String(256))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user = relationship("User", back_populates="ocr_config")
