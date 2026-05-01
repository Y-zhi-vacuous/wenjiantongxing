"""
学生写作能力分析服务
每次批改后自动更新，从 AI 报告中提取个性化反馈
"""
from sqlalchemy import select
from app.db import async_session
from app.models import Essay, EssayReport, StudentAbility


# 五项维度满分（对应新的评分体系）
MAX_SCORES = {
    "thesis": 10,
    "content": 15,
    "language": 10,
    "structure": 5,
    "penmanship": 5,
}


async def update_student_ability(essay_id: int):
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

        # 获取该学生所有已批改的作文
        history_result = await db.execute(
            select(Essay).where(Essay.student_id == essay.student_id, Essay.status == "graded")
        )
        all_essays = history_result.scalars().all()

        # 获取或创建能力记录
        ability_result = await db.execute(
            select(StudentAbility).where(StudentAbility.student_id == essay.student_id)
        )
        ability = ability_result.scalar_one_or_none()
        if not ability:
            ability = StudentAbility(student_id=essay.student_id)
            db.add(ability)

        # 构建分数历史（含五项维度）
        score_history = []
        all_suggestions = []
        all_comments = []
        for e in all_essays:
            rep = await db.execute(select(EssayReport).where(EssayReport.essay_id == e.id))
            r = rep.scalar_one_or_none()
            if r:
                score_history.append({
                    "essay_id": e.id,
                    "date": str(e.submitted_at.date()) if e.submitted_at else "",
                    "title": e.title,
                    "total_score": r.total_score,
                    "thesis": r.score_thesis,
                    "content": r.score_content,
                    "language": r.score_language,
                    "structure": r.score_structure,
                    "penmanship": r.score_penmanship,
                })
                # 收集 AI 的点评和建议
                if r.suggestions:
                    all_suggestions.extend(r.suggestions)
                if r.overall_comment:
                    all_comments.append(r.overall_comment)

        n = len(score_history)
        ability.overall_score = round(sum(h["total_score"] for h in score_history) / n, 1) if n > 0 else 0
        ability.essay_count = n

        # 五维能力值（百分制）
        for dim, mx in MAX_SCORES.items():
            scores = [h[dim] / mx * 100 for h in score_history]
            setattr(ability, f"{dim}_ability", round(sum(scores) / n, 1))

        ability.score_history = score_history

        # 优劣势：基于最新的五维能力值
        dims = [
            ("立意能力", ability.thesis_ability),
            ("内容能力", ability.content_ability),
            ("语言能力", ability.language_ability),
            ("结构能力", ability.structure_ability),
            ("文面能力", ability.penmanship_ability),
        ]
        dims.sort(key=lambda x: x[1], reverse=True)
        ability.strengths = [d[0] for d in dims[:2]]
        ability.weaknesses = [d[0] for d in dims[-2:]]

        # 从 AI 报告中提取个性化改进建议
        ability.improvement_plan = _build_personalized_plan(
            ability, score_history, all_suggestions, all_comments
        )

        # 词汇统计
        total_words = sum(e.word_count or 0 for e in all_essays)
        ability.vocabulary_stats = {
            "avg_word_count": round(total_words / n) if n > 0 else 0,
            "total_words": total_words,
            "essay_count": n,
        }

        ability.last_essay_id = essay_id
        await db.commit()


def _build_personalized_plan(ability, history, all_suggestions, all_comments) -> list:
    """基于 AI 历史点评生成个性化改进计划"""
    plans = []

    # 合并来自 AI 报告的真实建议，去重并按维度归类
    dim_keywords = {
        "立意能力": ["立意", "审题", "主题", "切题", "偏题", "离题", "角度", "观点"],
        "内容能力": ["内容", "素材", "细节", "描写", "选材", "事例", "具体", "空泛", "详略"],
        "语言能力": ["语言", "表达", "修辞", "文采", "词", "句", "流畅", "生动", "通顺"],
        "结构能力": ["结构", "开头", "结尾", "过渡", "段落", "层次", "呼应", "条理"],
        "文面能力": ["卷面", "标点", "错别字", "书写", "字数", "格式", "规范"],
    }

    for dim_name, keywords in dim_keywords.items():
        score = getattr(ability, f"{dim_name[:4]}_ability".replace("文面", "penmanship").replace("内容", "content").replace("立意", "thesis").replace("语言", "language").replace("结构", "structure"), 50) if True else 50

        # Map dim_name to ability attribute
        dim_map = {"立意能力": "thesis", "内容能力": "content", "语言能力": "language", "结构能力": "structure", "文面能力": "penmanship"}
        score = getattr(ability, f"{dim_map[dim_name]}_ability", 50)

        # 从 AI 反馈中找匹配的建议
        matched = []
        for s in all_suggestions:
            if any(kw in s for kw in keywords):
                matched.append(s)

        if matched:
            level = "优秀" if score >= 85 else "中等偏上" if score >= 70 else "亟待提升"
            plans.append({
                "dimension": dim_name,
                "level": level,
                "score": score,
                "suggestions": matched[:3],  # 最多 3 条来自 AI 的真实建议
            })
        else:
            level = "优秀" if score >= 85 else "中等偏上" if score >= 70 else "亟待提升"
            plans.append({
                "dimension": dim_name,
                "level": level,
                "score": score,
                "suggestions": [_default_suggestion(dim_name, score)],
            })

    # 总体趋势
    if len(history) >= 2:
        recent = history[-3:] if len(history) >= 3 else history
        trend = recent[-1]["total_score"] - recent[0]["total_score"]
        if trend > 3:
            plans.append({"dimension": "整体趋势", "level": "明显进步", "score": trend,
                         "suggestions": ["保持当前学习方法，可以尝试更高难度题目"]})
        elif trend < -2:
            plans.append({"dimension": "整体趋势", "level": "有所下滑", "score": trend,
                         "suggestions": ["回顾近期失分点，针对薄弱项进行专项训练"]})

    return plans


def _default_suggestion(dim_name: str, score: float) -> str:
    """兜底建议——当 AI 没有针对该维度的具体反馈时"""
    tips = {
        "立意能力": "每次写作前花2分钟审题，圈出题目关键词，确保文章围绕核心主题展开",
        "内容能力": "用具体事例和感官细节替代概括性叙述，让读者能'看见'你写的内容",
        "语言能力": "尝试在每段中使用至少一种修辞手法（比喻、拟人、排比），增强表达力",
        "结构能力": "动笔前列出3-5点提纲（开头→事件→转折→感悟→结尾），保证结构完整",
        "文面能力": "写完后通读一遍，检查标点符号和常见错别字，保持卷面整洁",
    }
    return tips.get(dim_name, "继续努力，坚持练习")
