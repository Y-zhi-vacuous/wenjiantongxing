"""
评分配置模型 — 教师端

v2.0: 从 AIConfig 拆分，包含评分模型和能力分析模型配置。
教师可选择付费 API（Zhipu/OpenAI/DeepSeek/Claude）或本地部署（Ollama/vLLM）。
"""
from sqlalchemy import String, Boolean, Enum as SAEnum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db import Base


class GradingProvider(str, enum.Enum):
    zhipu = "zhipu"
    openai = "openai"
    deepseek = "deepseek"
    claude = "claude"
    ollama = "ollama"
    vllm = "vllm"


class GradingConfig(Base):
    __tablename__ = "grading_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False, index=True)
    provider: Mapped[GradingProvider] = mapped_column(SAEnum(GradingProvider), default=GradingProvider.zhipu)
    grading_model_name: Mapped[str] = mapped_column(String(64), default="GLM-4-Flash-250414")
    ability_model_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    api_key_encrypted: Mapped[str | None] = mapped_column(String(512))
    base_url: Mapped[str | None] = mapped_column(String(256))
    local_endpoint_url: Mapped[str | None] = mapped_column(String(256))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user = relationship("User", back_populates="grading_config")
