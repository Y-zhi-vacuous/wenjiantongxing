"""
作文 API — v2.0

v2.0 变化:
  - 评分触发改为教师专有 (POST /essays/{id}/grade 需 teacher 角色)
  - 新增 GET /essays/ungraded 教师查看未评分作文
  - 新增 POST /essays/grade-all 一键全部评分 (串行逐篇)
  - OCR 上传传递 student_id 用于读取学生 OCR 配置
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db import get_db, async_session
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


@router.post("/upload-image", response_model=EssayResponse)
async def upload_image_essay(
    file: UploadFile = File(...),
    topic_id: int = Form(...),
    title: str = Form("未命名作文"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """v2.0: 上传手写作文图片 — 使用学生 OCR 配置"""
    content_bytes = await file.read()
    content = await parse_image_to_text_async(content_bytes, student_id=user.id)
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


# ──────────────────────────────────────────────
# v2.0: 教师触发评分
# ──────────────────────────────────────────────

@router.post("/{essay_id}/grade")
async def trigger_grading(
    essay_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """v2.0: 教师触发单篇评分"""
    if user.role.value != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可触发批改")

    result = await db.execute(select(Essay).where(Essay.id == essay_id))
    essay = result.scalar_one_or_none()
    if not essay:
        raise HTTPException(status_code=404, detail="作文不存在")
    if essay.status == EssayStatus.grading:
        raise HTTPException(status_code=400, detail="该作文正在批改中")

    essay.status = EssayStatus.grading
    essay.grading_requested_at = func.now()
    await db.commit()

    from app.services.grading import grade_essay
    import asyncio
    asyncio.create_task(grade_essay(essay_id, teacher_id=user.id))

    return {"message": "批改已开始", "essay_id": essay_id}


# ──────────────────────────────────────────────
# v2.0: 未评分作文列表 + 一键全部评分
# ──────────────────────────────────────────────

@router.get("/list/ungraded", response_model=list[EssayResponse])
async def list_ungraded_essays(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """v2.0: 教师查看所有未评分作文（含已提交和新上传的）"""
    if user.role.value != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可查看未评分列表")

    result = await db.execute(
        select(Essay)
        .where(Essay.status.in_([EssayStatus.submitted, EssayStatus.draft]))
        .options(joinedload(Essay.topic))
        .order_by(Essay.submitted_at.desc())
    )
    essays = result.scalars().all()
    return [EssayResponse.model_validate(e) for e in essays]


@router.post("/grade-all")
async def grade_all_ungraded(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """v2.0: 教师一键全部评分 — 串行逐篇处理"""
    if user.role.value != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可触发批改")

    result = await db.execute(
        select(Essay).where(
            Essay.status.in_([EssayStatus.submitted, EssayStatus.draft])
        )
    )
    essays = result.scalars().all()

    if not essays:
        return {"message": "没有待批改的作文", "total": 0, "graded": 0}

    from app.services.grading import grade_essay
    import asyncio as aio

    graded_ids = []

    async def grade_sequentially():
        for essay in essays:
            try:
                # 设置状态为 grading
                async with async_session() as s:
                    e_result = await s.execute(select(Essay).where(Essay.id == essay.id))
                    e = e_result.scalar_one_or_none()
                    if e and e.status != EssayStatus.grading:
                        e.status = EssayStatus.grading
                        e.grading_requested_at = func.now()
                        await s.commit()
                await grade_essay(essay.id, teacher_id=user.id)
                graded_ids.append(essay.id)
            except Exception as e:
                print(f"[GRADE-ALL] 作文 {essay.id} 批改失败: {e}")

    aio.create_task(grade_sequentially())

    return {
        "message": f"开始批改 {len(essays)} 篇作文（逐篇串行处理）",
        "total": len(essays),
        "graded": 0,
    }


