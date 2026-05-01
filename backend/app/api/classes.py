from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User, Class, ClassStudent, Essay
from app.schemas import ClassCreate, ClassResponse, AddStudentRequest
from app.auth import get_current_user

router = APIRouter(prefix="/classes", tags=["班级"])


@router.get("", response_model=list[ClassResponse])
async def list_classes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.role.value == "teacher":
        result = await db.execute(select(Class).where(Class.teacher_id == user.id))
    else:
        result = await db.execute(
            select(Class).join(ClassStudent).where(ClassStudent.student_id == user.id)
        )
    return [ClassResponse.model_validate(c) for c in result.scalars().all()]


@router.post("", response_model=ClassResponse)
async def create_class(
    req: ClassCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.role.value != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可创建班级")
    cls = Class(name=req.name, teacher_id=user.id)
    db.add(cls)
    await db.commit()
    await db.refresh(cls)
    return ClassResponse.model_validate(cls)


@router.get("/{class_id}", response_model=ClassResponse)
async def get_class(class_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Class).where(Class.id == class_id))
    cls = result.scalar_one_or_none()
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")
    return ClassResponse.model_validate(cls)


@router.get("/{class_id}/students")
async def list_students(class_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User, ClassStudent).join(ClassStudent).where(ClassStudent.class_id == class_id)
    )
    students = []
    for user, cs in result:
        essay_count = await db.scalar(
            select(func.count(Essay.id)).where(Essay.student_id == user.id)
        )
        students.append({
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "essay_count": essay_count,
        })
    return {"students": students}


@router.post("/{class_id}/students")
async def add_student(
    class_id: int,
    req: AddStudentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.role.value != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可添加学生")
    student_result = await db.execute(select(User).where(User.username == req.username))
    student = student_result.scalar_one_or_none()
    if not student or student.role.value != "student":
        raise HTTPException(status_code=400, detail="学生不存在")
    existing = await db.execute(
        select(ClassStudent).where(
            ClassStudent.class_id == class_id, ClassStudent.student_id == student.id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="学生已在班级中")
    cs = ClassStudent(class_id=class_id, student_id=student.id)
    db.add(cs)
    await db.commit()
    return {"message": "添加成功"}
