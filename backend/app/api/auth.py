from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User, UserRole, ClassStudent
from app.models.user import User as UserModel
from app.schemas.auth import (
    TeacherRegisterRequest, StudentCreateRequest,
    PasswordChangeRequest, UserResponse, AuthResponse,
)
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register/teacher", status_code=status.HTTP_201_CREATED)
async def register_teacher(req: TeacherRegisterRequest, db: AsyncSession = Depends(get_db)):
    """教师实名注册"""
    existing = await db.execute(select(User).where(User.username == req.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")
    teacher = User(
        username=req.username,
        password_hash=hash_password(req.password),
        role=UserRole.teacher,
        display_name=req.display_name,
        real_name=req.real_name,
        school=req.school,
        teacher_cert=req.teacher_cert,
    )
    db.add(teacher)
    await db.commit()
    return {"message": "教师注册成功，请登录"}


@router.post("/register/student", status_code=status.HTTP_201_CREATED)
async def create_student(
    req: StudentCreateRequest,
    teacher: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """教师为学生创建账号并自动加入班级"""
    if teacher.role.value != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可创建学生账号")

    existing = await db.execute(select(User).where(User.username == req.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    student = User(
        username=req.username,
        password_hash=hash_password(req.password),
        default_password=req.password,  # 记录默认密码(明文)
        role=UserRole.student,
        display_name=req.display_name,
        school=teacher.school,
        grade="九年级",
    )
    db.add(student)
    await db.flush()

    # 自动加入教师班级
    cs = ClassStudent(class_id=req.class_id, student_id=student.id)
    db.add(cs)
    await db.commit()
    return {"message": f"学生账号 {req.username} 创建成功，默认密码: {req.password}"}


@router.put("/password")
async def change_password(
    req: PasswordChangeRequest,
    user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """学生修改密码"""
    if not verify_password(req.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    user.password_hash = hash_password(req.new_password)
    user.default_password = None  # 清除默认密码标记
    await db.commit()
    return {"message": "密码修改成功"}


@router.post("/login", response_model=AuthResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token(user.id)
    return AuthResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
async def me(user: UserModel = Depends(get_current_user)):
    return UserResponse.model_validate(user)
