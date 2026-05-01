from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User, StudentAbility
from app.auth import get_current_user

router = APIRouter(prefix="/ability", tags=["能力分析"])


@router.get("/me")
async def get_my_ability(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """学生查看自己的写作能力画像"""
    result = await db.execute(
        select(StudentAbility).where(StudentAbility.student_id == user.id)
    )
    ability = result.scalar_one_or_none()
    if not ability:
        return {
            "student_id": user.id,
            "display_name": user.display_name,
            "essay_count": 0,
            "message": "提交第一篇作文并获得批改后，将生成你的能力画像",
        }
    return {
        "student_id": ability.student_id,
        "display_name": user.display_name,
        "overall_score": ability.overall_score,
        "essay_count": ability.essay_count,
        "abilities": {
            "content": ability.content_ability,
            "language": ability.language_ability,
            "structure": ability.structure_ability,
            "penmanship": ability.penmanship_ability,
        },
        "score_history": ability.score_history,
        "strengths": ability.strengths,
        "weaknesses": ability.weaknesses,
        "improvement_plan": ability.improvement_plan,
        "vocabulary_stats": ability.vocabulary_stats,
        "last_updated": str(ability.last_updated) if ability.last_updated else None,
    }


@router.get("/student/{student_id}")
async def get_student_ability(
    student_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """教师查看指定学生的写作能力画像"""
    if user.role.value != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可查看学生能力")

    ability_result = await db.execute(
        select(StudentAbility).where(StudentAbility.student_id == student_id)
    )
    ability = ability_result.scalar_one_or_none()

    student_result = await db.execute(select(User).where(User.id == student_id))
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    if not ability:
        return {
            "student_id": student_id,
            "display_name": student.display_name,
            "username": student.username,
            "essay_count": 0,
            "message": "该学生尚未提交作文或未有批改记录",
        }

    return {
        "student_id": student_id,
        "display_name": student.display_name,
        "username": student.username,
        "overall_score": ability.overall_score,
        "essay_count": ability.essay_count,
        "abilities": {
            "content": ability.content_ability,
            "language": ability.language_ability,
            "structure": ability.structure_ability,
            "penmanship": ability.penmanship_ability,
        },
        "score_history": ability.score_history,
        "strengths": ability.strengths,
        "weaknesses": ability.weaknesses,
        "improvement_plan": ability.improvement_plan,
        "vocabulary_stats": ability.vocabulary_stats,
        "last_updated": str(ability.last_updated) if ability.last_updated else None,
    }
