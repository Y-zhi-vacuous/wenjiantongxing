from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db import get_db
from app.models import User, Essay, EssayStatus, EssayReport
from app.schemas import EssayCreate, EssayResponse, ReportResponse
from app.auth import get_current_user
from app.services.parsing import parse_file_content, parse_image_to_text_async

router = APIRouter(prefix="/essays", tags=["作文"])


@router.post("", response_model=EssayResponse)
async def create_essay(
    req: EssayCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    essay = Essay(
        student_id=user.id,
        topic_id=req.topic_id,
        title=req.title,
        content=req.content,
        word_count=len(req.content),
        status=EssayStatus.submitted,
    )
    db.add(essay)
    await db.commit()
    await db.refresh(essay)
    return EssayResponse.model_validate(essay)


@router.post("/upload", response_model=EssayResponse)
async def upload_essay(
    file: UploadFile = File(...),
    topic_id: int = Form(...),
    title: str = Form("未命名作文"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content_bytes = await file.read()
    content = parse_file_content(content_bytes, file.filename or "")
    essay = Essay(
        student_id=user.id,
        topic_id=topic_id,
        title=title,
        content=content,
        word_count=len(content),
        status=EssayStatus.submitted,
    )
    db.add(essay)
    await db.commit()
    await db.refresh(essay)
    return EssayResponse.model_validate(essay)


@router.get("/{essay_id}", response_model=EssayResponse)
async def get_essay(
    essay_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Essay).where(Essay.id == essay_id).options(joinedload(Essay.topic))
    )
    essay = result.scalar_one_or_none()
    if not essay:
        raise HTTPException(status_code=404, detail="作文不存在")
    return EssayResponse.model_validate(essay)


@router.get("", response_model=list[EssayResponse])
async def list_essays(
    limit: int = 50,
    status: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Essay).options(joinedload(Essay.topic))
    if user.role.value == "student":
        query = query.where(Essay.student_id == user.id)
    if status:
        query = query.where(Essay.status == status)
    query = query.order_by(Essay.submitted_at.desc()).limit(limit)
    result = await db.execute(query)
    essays = result.scalars().all()
    return [EssayResponse.model_validate(e) for e in essays]


@router.get("/{essay_id}/report", response_model=ReportResponse | None)
async def get_report(
    essay_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(EssayReport).where(EssayReport.essay_id == essay_id))
    report = result.scalar_one_or_none()
    if not report:
        return None
    return ReportResponse.model_validate(report)


@router.post("/upload-image", response_model=EssayResponse)
async def upload_image_essay(
    file: UploadFile = File(...),
    topic_id: int = Form(...),
    title: str = Form("未命名作文"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传手写作文图片"""
    content_bytes = await file.read()
    filename = file.filename or "essay.png"
    content = await parse_image_to_text_async(content_bytes)
    essay = Essay(
        student_id=user.id,
        topic_id=topic_id,
        title=title,
        content=content,
        word_count=len(content),
        status=EssayStatus.submitted,
    )
    db.add(essay)
    await db.commit()
    await db.refresh(essay)
    return EssayResponse.model_validate(essay)


@router.post("/{essay_id}/grade")
async def trigger_grading(
    essay_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Essay).where(Essay.id == essay_id))
    essay = result.scalar_one_or_none()
    if not essay:
        raise HTTPException(status_code=404, detail="作文不存在")
    essay.status = EssayStatus.grading
    await db.commit()

    from app.services.grading import grade_essay
    import asyncio
    asyncio.create_task(grade_essay(essay_id))

    return {"message": "批改已开始", "essay_id": essay_id}
