from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User, EssayTopic, TopicSource
from app.schemas import TopicCreate, TopicResponse
from app.auth import get_current_user

router = APIRouter(prefix="/topics", tags=["题库"])


@router.get("", response_model=list[TopicResponse])
async def list_topics(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EssayTopic).order_by(EssayTopic.created_at.desc()))
    return [TopicResponse.model_validate(t) for t in result.scalars().all()]


@router.post("", response_model=TopicResponse)
async def create_topic(
    req: TopicCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.role.value != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可添加题目")
    topic = EssayTopic(
        title=req.title,
        type=req.type,
        genre=req.genre,
        difficulty=req.difficulty,
        tips=req.tips,
        word_requirement=req.word_requirement,
        time_minutes=req.time_minutes,
        extra_requirements=req.extra_requirements,
        source=TopicSource.teacher,
        creator_id=user.id,
    )
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    return TopicResponse.model_validate(topic)


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EssayTopic).where(EssayTopic.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="题目不存在")
    return TopicResponse.model_validate(topic)
