from sqlalchemy import String, Boolean, Enum as SAEnum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db import Base


class RoutingStrategy(str, enum.Enum):
    smart = "smart"
    cloud = "cloud"
    local = "local"


class AIConfig(Base):
    __tablename__ = "ai_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(32), default="zhipu")
    model_name: Mapped[str] = mapped_column(String(64), default="GLM-4-Flash-250414")
    grading_model_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ocr_model_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    api_key_encrypted: Mapped[str | None] = mapped_column(String(512))
    routing_strategy: Mapped[RoutingStrategy] = mapped_column(SAEnum(RoutingStrategy), default=RoutingStrategy.smart)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user = relationship("User", back_populates="ai_config")
