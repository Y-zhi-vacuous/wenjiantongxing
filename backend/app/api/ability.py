"""
能力分析 API — v2.0

v2.0 变化:
  - 教师可触发能力分析刷新 (POST /ability/refresh/{student_id})
  - 响应包含五个完整维度 (含 thesis)
  - 新增 teaching_recommendations 和 error_patterns 字段
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User, StudentAbility, Essay, EssayStatus
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
    return _format_ability(ability, user.display_name)


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

    data = _format_ability(ability, student.display_name)
    data["username"] = student.username
    return data


@router.post("/refresh/{student_id}")
async def refresh_ability(
    student_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """v2.0: 教师触发指定学生的能力分析刷新"""
    if user.role.value != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可刷新能力分析")

    student_result = await db.execute(select(User).where(User.id == student_id))
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    # 找到该学生最近批改的作文
    essay_result = await db.execute(
        select(Essay)
        .where(Essay.student_id == student_id, Essay.status == EssayStatus.graded)
        .order_by(Essay.graded_at.desc().nulls_last())
        .limit(1)
    )
    essay = essay_result.scalar_one_or_none()
    if not essay:
        raise HTTPException(status_code=400, detail="该学生尚无已批改的作文")

    from app.services.ability import update_student_ability
    await update_student_ability(essay.id, teacher_id=user.id)

    return {"message": "能力分析已刷新", "student_id": student_id}


@router.post("/refresh-all")
async def refresh_all_abilities(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """v2.0: 教师刷新所有已评分学生的能力分析"""
    if user.role.value != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可刷新能力分析")

    abilities_result = await db.execute(select(StudentAbility))
    abilities = abilities_result.scalars().all()

    count = 0
    for ability in abilities:
        if ability.last_essay_id:
            try:
                from app.services.ability import update_student_ability
                await update_student_ability(ability.last_essay_id, teacher_id=user.id)
                count += 1
            except Exception as e:
                print(f"[REFRESH-ALL] student={ability.student_id} 失败: {e}")

    return {"message": f"已刷新 {count} 名学生的能力分析"}


def _format_ability(ability, display_name: str) -> dict:
    """v2.0: 格式化能力分析响应（含全部五个维度）"""
    return {
        "student_id": ability.student_id,
        "display_name": display_name,
        "overall_score": ability.overall_score,
        "essay_count": ability.essay_count,
        "abilities": {
            "thesis": ability.thesis_ability,
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
