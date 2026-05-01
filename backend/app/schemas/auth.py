from pydantic import BaseModel


class TeacherRegisterRequest(BaseModel):
    """教师实名注册"""
    username: str
    password: str
    display_name: str
    real_name: str          # 真实姓名
    school: str             # 任教学校
    teacher_cert: str       # 教师资格证号


class StudentCreateRequest(BaseModel):
    """教师为学生创建账号"""
    username: str
    password: str
    display_name: str
    class_id: int


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    display_name: str
    real_name: str | None = None
    school: str | None = None
    grade: str | None = None

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
