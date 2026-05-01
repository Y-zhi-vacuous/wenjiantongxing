"""
学生写作能力分析服务
每次批改完成后自动更新学生能力画像
"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session
from app.models import Essay, EssayReport, StudentAbility


async def update_student_ability(essay_id: int):
    """根据最新批改结果，更新学生能力画像"""
    async with async_session() as db:
        essay_result = await db.execute(select(Essay).where(Essay.id == essay_id))
        essay = essay_result.scalar_one_or_none()
        if not essay or essay.status.value != "graded":
            return

        report_result = await db.execute(
            select(EssayReport).where(EssayReport.essay_id == essay_id)
        )
        report = report_result.scalar_one_or_none()
        if not report:
            return

        # 获取该学生所有历史和能力记录
        history_result = await db.execute(
            select(Essay).where(
                Essay.student_id == essay.student_id,
                Essay.status == "graded"
            )
        )
        all_essays = history_result.scalars().all()

        ability_result = await db.execute(
            select(StudentAbility).where(StudentAbility.student_id == essay.student_id)
        )
        ability = ability_result.scalar_one_or_none()

        if not ability:
            ability = StudentAbility(student_id=essay.student_id)
            db.add(ability)

        # 构建分数历史
        score_history = []
        for e in all_essays:
            rep = await db.execute(select(EssayReport).where(EssayReport.essay_id == e.id))
            r = rep.scalar_one_or_none()
            if r:
                score_history.append({
                    "essay_id": e.id,
                    "date": str(e.submitted_at.date()) if e.submitted_at else "",
                    "title": e.title,
                    "total_score": r.total_score,
                    "content": r.score_content,
                    "language": r.score_language,
                    "structure": r.score_structure,
                    "penmanship": r.score_penmanship,
                })

        total = sum(h["total_score"] for h in score_history)
        n = len(score_history)
        ability.overall_score = round(total / n, 1) if n > 0 else report.total_score
        ability.essay_count = n

        # 四维能力 (百分制: 各项满分 → 100)
        max_scores = {"content": 20, "language": 15, "structure": 10, "penmanship": 5}
        content_scores = [h["content"] / max_scores["content"] * 100 for h in score_history]
        lang_scores = [h["language"] / max_scores["language"] * 100 for h in score_history]
        struct_scores = [h["structure"] / max_scores["structure"] * 100 for h in score_history]
        pen_scores = [h["penmanship"] / max_scores["penmanship"] * 100 for h in score_history]

        ability.content_ability = round(sum(content_scores) / n, 1)
        ability.language_ability = round(sum(lang_scores) / n, 1)
        ability.structure_ability = round(sum(struct_scores) / n, 1)
        ability.penmanship_ability = round(sum(pen_scores) / n, 1)

        ability.score_history = score_history

        # 优劣势分析
        dims = [
            ("内容能力", ability.content_ability),
            ("语言能力", ability.language_ability),
            ("结构能力", ability.structure_ability),
            ("卷面能力", ability.penmanship_ability),
        ]
        dims.sort(key=lambda x: x[1], reverse=True)
        ability.strengths = [dim[0] for dim in dims[:2]]
        ability.weaknesses = [dim[0] for dim in dims[-2:]]

        # 生成改进建议
        improvement_plan = _generate_improvements(ability, score_history)
        ability.improvement_plan = improvement_plan

        # 词汇统计
        total_words = sum(e.word_count for e in all_essays) if all_essays else 0
        ability.vocabulary_stats = {
            "avg_word_count": round(total_words / n) if n > 0 else 0,
            "total_words": total_words,
            "essay_count": n,
        }

        ability.last_essay_id = essay_id
        ability.last_updated = func.now()
        await db.commit()


def _generate_improvements(ability: StudentAbility, history: list) -> list:
    """基于能力数据生成结构化改进建议"""
    plans = []

    # 内容能力分析
    ca = ability.content_ability
    if ca < 60:
        plans.append({
            "dimension": "内容能力",
            "level": "亟待提升",
            "score": ca,
            "suggestions": [
                "加强审题训练，拿到题目先圈关键词，确保不偏题",
                "素材积累：每天记录1个身边小事，建立个人素材库",
                "练习'以小见大'：从平凡小事中挖掘深层含义",
            ],
        })
    elif ca < 80:
        plans.append({
            "dimension": "内容能力",
            "level": "中等偏上",
            "score": ca,
            "suggestions": [
                "在选材上追求'独特视角'，避免泛泛而谈",
                "加强立意深度：多问自己'这件事为什么重要'",
                "适当引用名言或诗词，提升文章格调",
            ],
        })
    else:
        plans.append({
            "dimension": "内容能力",
            "level": "优秀",
            "score": ca,
            "suggestions": [
                "尝试更有挑战性的题材和视角",
                "关注社会热点，拓展写作视野",
                "保持优势，稳中求新",
            ],
        })

    # 语言能力分析
    la = ability.language_ability
    if la < 60:
        plans.append({
            "dimension": "语言能力",
            "level": "亟待提升",
            "score": la,
            "suggestions": [
                "精读优秀范文，摘抄好词好句，每周不少于5句",
                "练习描写：每天用50字描写一个场景，至少用2个感官",
                "减少概括性叙述，多用具体动作和对话推进故事",
            ],
        })
    elif la < 80:
        plans.append({
            "dimension": "语言能力",
            "level": "中等偏上",
            "score": la,
            "suggestions": [
                "丰富修辞手法：比喻、拟人、排比交替使用",
                "注意词语的精准度，避免'很好''很美'等空洞词",
                "尝试不同的句式节奏（长句+短句交替）",
            ],
        })
    else:
        plans.append({
            "dimension": "语言能力",
            "level": "优秀",
            "score": la,
            "suggestions": [
                "追求语言风格的辨识度",
                "在准确的基础上追求文采和意境",
                "可尝试文学性写作训练",
            ],
        })

    # 结构能力分析
    sa = ability.structure_ability
    if sa < 60:
        plans.append({
            "dimension": "结构能力",
            "level": "亟待提升",
            "score": sa,
            "suggestions": [
                "动笔前先列提纲（开头→主体→结尾各写什么）",
                "练习'凤头—猪肚—豹尾'的经典结构",
                "注意段落间过渡，避免跳跃太大",
            ],
        })
    elif sa < 80:
        plans.append({
            "dimension": "结构能力",
            "level": "中等偏上",
            "score": sa,
            "suggestions": [
                "开头尝试多种方式（场景式/悬念式/引用式）",
                "结尾练习'回味式'写法，让文章有留白",
                "注意详略得当，重点段落要充分展开",
            ],
        })
    else:
        plans.append({
            "dimension": "结构能力",
            "level": "优秀",
            "score": sa,
            "suggestions": [
                "探索更灵活的结构（倒叙/插叙/双线）",
                "在完整的基础上追求结构的创意",
            ],
        })

    # 总体趋势分析
    if len(history) >= 3:
        recent = history[-3:]
        trend = recent[-1]["total_score"] - recent[0]["total_score"]
        if trend > 3:
            plans.append({
                "dimension": "整体趋势",
                "level": "明显进步",
                "score": trend,
                "suggestions": ["保持当前学习方法，继续积累", "可以适当提高题目难度"],
            })
        elif trend < -2:
            plans.append({
                "dimension": "整体趋势",
                "level": "有所下滑",
                "score": trend,
                "suggestions": ["回顾近期失分点，找准问题根源", "适当降低难度，建立信心"],
            })

    return plans
