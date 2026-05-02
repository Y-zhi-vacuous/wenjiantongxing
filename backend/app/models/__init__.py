from app.models.user import User, UserRole
from app.models.essay import Essay, EssayStatus
from app.models.topic import EssayTopic, TopicType, TopicGenre, TopicSource
from app.models.report import EssayReport
from app.models.ai_config import AIConfig, RoutingStrategy  # deprecated v2.0
from app.models.ocr_config import OCRConfig
from app.models.grading_config import GradingConfig, GradingProvider
from app.models.class_ import Class, ClassStudent
from app.models.ability import StudentAbility
from app.models.feedback import EssayFeedback
from app.db import Base
