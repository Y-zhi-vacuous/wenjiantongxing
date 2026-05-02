"""
评分配置模型 — 教师端 (v2.0)

评分模型和能力分析模型可分别配置不同的提供商、模型名称和 API Key。
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

    # 评分模型配置
    grading_use_default: Mapped[bool] = mapped_column(Boolean, default=True)
    grading_provider: Mapped[GradingProvider] = mapped_column(SAEnum(GradingProvider), default=GradingProvider.zhipu)
    grading_model_name: Mapped[str] = mapped_column(String(64), default="GLM-4-Flash-250414")
    grading_api_key: Mapped[str | None] = mapped_column(String(512))
    grading_base_url: Mapped[str | None] = mapped_column(String(256))
    grading_local_url: Mapped[str | None] = mapped_column(String(256))

    # 能力分析模型配置（独立，可选不同于评分模型的提供商）
    ability_use_default: Mapped[bool] = mapped_column(Boolean, default=True)
    ability_provider: Mapped[GradingProvider | None] = mapped_column(SAEnum(GradingProvider), nullable=True)
    ability_model_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ability_api_key: Mapped[str | None] = mapped_column(String(512))
    ability_base_url: Mapped[str | None] = mapped_column(String(256))
    ability_local_url: Mapped[str | None] = mapped_column(String(256))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # 兼容旧字段（deprecated）
    provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    api_key_encrypted: Mapped[str | None] = mapped_column(String(512))
    base_url: Mapped[str | None] = mapped_column(String(256))
    local_endpoint_url: Mapped[str | None] = mapped_column(String(256))

    user = relationship("User", back_populates="grading_config")
