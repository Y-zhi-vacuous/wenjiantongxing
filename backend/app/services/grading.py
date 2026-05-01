import time
import traceback
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db import async_session
from app.models import Essay, EssayStatus, EssayReport
from app.agents.grader import run_grader


async def grade_essay(essay_id: int):
    start = time.time()
    async with async_session() as db:
        try:
            result = await db.execute(
                select(Essay).where(Essay.id == essay_id).options(joinedload(Essay.topic))
            )
            essay = result.scalar_one_or_none()
            if not essay:
                return

            content = essay.content or ""
            topic = essay.topic

            # 内容质量校验
            if "[手写作文" in content and "OCR" in content:
                report = EssayReport(
                    essay_id=essay.id, total_score=0,
                    score_thesis=0, score_content=0, score_language=0,
                    score_structure=0, score_penmanship=0,
                    overall_comment="OCR 识别失败，无法批改。请确认图片清晰度后重新上传。",
                    suggestions=["请重新拍摄或上传更清晰的手写作文图片"],
                    model_used="system", processing_time_ms=0,
                )
                db.add(report)
                essay.status = EssayStatus.graded
                await db.commit()
                return
            if len(content) < 100:
                report = EssayReport(
                    essay_id=essay.id, total_score=5,
                    score_thesis=1, score_content=2, score_language=1,
                    score_structure=1, score_penmanship=0,
                    overall_comment="文章字数严重不足，无法进行有效批改。中考作文要求不少于600字，建议重新提交完整作文。",
                    suggestions=["中考作文要求不少于600字，请补充完整内容后重新提交"],
                    model_used="system", processing_time_ms=0,
                )
                db.add(report)
                essay.status = EssayStatus.graded
                await db.commit()
                return

            # 构造题目信息
            topic_info = ""
            if topic:
                topic_info = f"作文题目：{topic.title}\n"
                if topic.tips:
                    topic_info += f"审题提示：{topic.tips}\n"
                if topic.extra_requirements:
                    topic_info += f"写作要求：{topic.extra_requirements}\n"
                topic_info += f"文体：{topic.genre.value}\n"

            report_data = await run_grader(content, topic_info=topic_info, user_id=essay.student_id)

            # 分数上限保护
            def clamp(v, mx):
                return max(0, min(float(v or 0), float(mx)))

            thesis = clamp(report_data.get("score_thesis", 0), 10)
            content_s = clamp(report_data.get("score_content", 0), 15)
            lang = clamp(report_data.get("score_language", 0), 10)
            struct = clamp(report_data.get("score_structure", 0), 5)
            pen = clamp(report_data.get("score_penmanship", 0), 5)

            # 切题判定直接影响总分
            topic_match = report_data.get("topic_match", "")
            if topic_match == "完全离题":
                thesis = min(thesis, 2)
                total = min(thesis + content_s + lang + struct + pen, 10)
            elif topic_match == "部分偏题":
                thesis = min(thesis, 5)
                total = min(thesis + content_s + lang + struct + pen, 29)
            else:
                total = clamp(report_data.get("total_score", 0), 45)

            # 五项和校验
            real_sum = thesis + content_s + lang + struct + pen
            if abs(total - real_sum) > 2:
                total = real_sum

            report = EssayReport(
                essay_id=essay.id,
                total_score=total,
                score_thesis=thesis,
                score_content=content_s,
                score_language=lang,
                score_structure=struct,
                score_penmanship=pen,
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

            try:
                from app.services.ability import update_student_ability
                await update_student_ability(essay_id)
            except Exception as e:
                print(f"[WARN] 能力分析更新失败 (essay={essay_id}): {e}")

        except Exception as e:
            print(f"[ERROR] 批改失败 (essay={essay_id}): {e}")
            traceback.print_exc()
            await db.rollback()
            essay_result = await db.execute(select(Essay).where(Essay.id == essay_id))
            essay = essay_result.scalar_one()
            if essay:
                essay.status = EssayStatus.submitted
                await db.commit()
