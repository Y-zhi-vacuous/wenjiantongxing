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

        # 从 AI 报告中生成个性化改进建议
        ability.improvement_plan = await _build_personalized_plan_async(
            ability, score_history, all_suggestions
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


ABILITY_SUMMARY_PROMPT = """你是深圳中考语文教学专家。请基于以下学生的历史作文评分数据，生成一份个性化的写作能力分析报告。

## 学生历史评分数据
{score_data}

## 学生各篇作文的 AI 批改建议
{suggestions_text}

## 要求
请输出 JSON 格式（不要用 ``` 包裹）：
{
  "overall_assessment": "该生写作能力的总体评价（80-150字），指出最关键的问题和最突出的优点",
  "dimensions": [
    {"dimension": "立意能力", "score": 数字(0-100), "assessment": "具体分析15-30字", "action_items": ["具体可执行的改进措施1", "措施2"]},
    {"dimension": "内容能力", "score": 数字(0-100), "assessment": "...", "action_items": ["..."]},
    {"dimension": "语言能力", "score": 数字(0-100), "assessment": "...", "action_items": ["..."]},
    {"dimension": "结构能力", "score": 数字(0-100), "assessment": "...", "action_items": ["..."]},
    {"dimension": "文面能力", "score": 数字(0-100), "assessment": "...", "action_items": ["..."]}
  ],
  "priority": "当前最急需改进的1-2个方面（15字以内）"
}"""


async def _build_personalized_plan_async(ability, history, all_suggestions) -> list:
    """使用 AI 生成个性化能力分析报告，降级到关键词匹配"""
    # 先尝试 AI 生成
    try:
        result = await _call_ability_ai(ability, history, all_suggestions)
        if result and len(result) >= 4:
            return result
    except Exception as e:
        print(f"[ABILITY] AI 生成失败: {e}")

    # 降级：关键词匹配
    return _build_keyword_plan(ability, history, all_suggestions)


async def _call_ability_ai(ability, history, all_suggestions):
    """调用 GLM-4 生成能力分析"""
    import httpx
    from app.config import get_settings

    settings = get_settings()
    api_key = settings.AI_API_KEY or "08291980aa0d44928db4cf142733edc4.Q41wSJGtwIy2IYmc"

    # 构造分数数据
    score_lines = []
    for h in history[-5:]:  # 最近 5 篇
        score_lines.append(
            f"- {h['date']} 《{h['title']}》: 总分{h['total_score']}(立意{h['thesis']}/内容{h['content']}/语言{h['language']}/结构{h['structure']}/文面{h['penmanship']})"
        )
    score_data = "\n".join(score_lines) if score_lines else "暂无数据"

    # 去重并取最近的建议
    seen = set()
    unique_suggestions = []
    for s in all_suggestions:
        key = s[:20]
        if key not in seen:
            seen.add(key)
            unique_suggestions.append(s)
    suggestions_text = "\n".join(f"- {s}" for s in unique_suggestions[:15])

    prompt = ABILITY_SUMMARY_PROMPT.replace("{score_data}", score_data).replace("{suggestions_text}", suggestions_text)

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            json={
                "model": "GLM-4-Flash-250414",
                "messages": [
                    {"role": "system", "content": "你是深圳中考语文教学专家，请基于学生历史数据生成个性化能力分析，输出JSON。"},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.5,
                "max_tokens": 2048,
            },
            headers={"Authorization": f"Bearer {api_key}"},
        )
        data = resp.json()
        if "choices" not in data:
            return None

        text = data["choices"][0]["message"]["content"].strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]

        import json
        ai_result = json.loads(text)

        plans = []
        # 总体评价
        if ai_result.get("overall_assessment"):
            plans.append({
                "dimension": "综合评估",
                "level": "",
                "score": ability.overall_score,
                "suggestions": [ai_result["overall_assessment"]],
            })
        if ai_result.get("priority"):
            plans.append({
                "dimension": "优先改进",
                "level": "",
                "score": 0,
                "suggestions": [ai_result["priority"]],
            })

        # 五维度分析
        for dim in ai_result.get("dimensions", []):
            plans.append({
                "dimension": dim.get("dimension", ""),
                "level": _score_to_level(dim.get("score", 50)),
                "score": dim.get("score", 50),
                "suggestions": [dim.get("assessment", "")] + dim.get("action_items", []),
            })

        # 趋势
        if len(history) >= 2:
            recent = history[-3:] if len(history) >= 3 else history
            trend = recent[-1]["total_score"] - recent[0]["total_score"]
            if abs(trend) > 1:
                plans.append({
                    "dimension": "整体趋势",
                    "level": "明显进步" if trend > 2 else "有所下滑",
                    "score": trend,
                    "suggestions": ["保持当前方法" if trend > 2 else "针对薄弱项专项训练"],
                })

        return plans


def _build_keyword_plan(ability, history, all_suggestions) -> list:
    """降级方案：关键词匹配"""
    plans = []
    dim_map = {"立意能力": "thesis", "内容能力": "content", "语言能力": "language", "结构能力": "structure", "文面能力": "penmanship"}
    dim_keywords = {
        "立意能力": ["立意", "审题", "主题", "切题", "偏题", "离题", "角度", "观点", "核心"],
        "内容能力": ["内容", "素材", "细节", "描写", "选材", "事例", "具体", "空泛", "详略"],
        "语言能力": ["语言", "表达", "修辞", "文采", "流畅", "生动", "通顺"],
        "结构能力": ["结构", "开头", "结尾", "过渡", "段落", "层次", "呼应", "条理"],
        "文面能力": ["卷面", "标点", "错别字", "书写", "字数", "格式", "规范"],
    }

    for dim_name, attr in dim_map.items():
        score = getattr(ability, f"{attr}_ability", 50)
        keywords = dim_keywords[dim_name]
        matched = list(dict.fromkeys([s for s in all_suggestions if any(kw in s for kw in keywords)]))
        plans.append({
            "dimension": dim_name,
            "level": _score_to_level(score),
            "score": score,
            "suggestions": matched[:3] if matched else [_fallback_tip(dim_name)],
        })

    if len(history) >= 2:
        recent = history[-3:] if len(history) >= 3 else history
        trend = recent[-1]["total_score"] - recent[0]["total_score"]
        if abs(trend) > 1:
            plans.append({
                "dimension": "整体趋势",
                "level": "明显进步" if trend > 2 else "有所下滑",
                "score": trend,
                "suggestions": ["保持当前方法" if trend > 2 else "针对薄弱项专项训练"],
            })
    return plans


def _score_to_level(score: float) -> str:
    if score >= 85: return "优秀"
    if score >= 70: return "中等偏上"
    if score >= 50: return "亟需提升"
    return "亟待加强"


def _fallback_tip(dim_name: str) -> str:
    tips = {
        "立意能力": "每次写作前花2分钟审题，圈出题目关键词，确保文章围绕核心主题展开",
        "内容能力": "用具体事例和感官细节替代概括性叙述",
        "语言能力": "每段使用至少一种修辞手法增强表达力",
        "结构能力": "动笔前列3-5点提纲保证结构完整",
        "文面能力": "写完后通读检查标点和错别字",
    }
    return tips.get(dim_name, "坚持练习")
