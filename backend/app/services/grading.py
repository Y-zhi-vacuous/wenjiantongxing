import time
import traceback
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session
from app.models import Essay, EssayStatus, EssayReport
from app.agents.grader import run_grader


async def grade_essay(essay_id: int):
    start = time.time()
    async with async_session() as db:
        try:
            result = await db.execute(select(Essay).where(Essay.id == essay_id))
            essay = result.scalar_one_or_none()
            if not essay:
                return

            report_data = await run_grader(essay.content, user_id=essay.student_id)

            report = EssayReport(
                essay_id=essay.id,
                total_score=report_data.get("total_score", 0),
                score_content=report_data.get("score_content", 0),
                score_language=report_data.get("score_language", 0),
                score_structure=report_data.get("score_structure", 0),
                score_penmanship=report_data.get("score_penmanship", 0),
                basic_errors=report_data.get("basic_errors"),
                paragraph_reviews=report_data.get("paragraph_reviews"),
                overall_comment=report_data.get("overall_comment"),
                suggestions=report_data.get("suggestions"),
                model_used=report_data.get("model_used", "mock"),
                processing_time_ms=int((time.time() - start) * 1000),
            )
            db.add(report)
            essay.status = EssayStatus.graded
            await db.commit()

            # 更新能力画像（独立事务，失败不影响批改结果）
            try:
                from app.services.ability import update_student_ability
                await update_student_ability(essay_id)
            except Exception as e:
                print(f"[WARN] 能力分析更新失败 (essay={essay_id}): {e}")
                traceback.print_exc()

        except Exception as e:
            print(f"[ERROR] 批改失败 (essay={essay_id}): {e}")
            traceback.print_exc()
            await db.rollback()
            # 重新获取 essay 并重置状态
            essay_result = await db.execute(select(Essay).where(Essay.id == essay_id))
            essay = essay_result.scalar_one()
            if essay:
                essay.status = EssayStatus.submitted
                await db.commit()
