from app.schemas.auth import (
    TeacherRegisterRequest, StudentCreateRequest, PasswordChangeRequest,
    LoginRequest, UserResponse, AuthResponse,
)
from app.schemas.essay import EssayCreate, EssayResponse, ReportResponse
from app.schemas.topic import TopicCreate, TopicResponse
from app.schemas.class_ import ClassCreate, ClassResponse, AddStudentRequest
from app.schemas.ai_config import AIConfigUpdate, AIConfigResponse
