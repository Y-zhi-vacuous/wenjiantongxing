"""
学生写作能力分析服务 (v2.0)

v2.0 变化:
  - 由教师触发 (update_student_ability 接受 teacher_id)
  - 使用教师 GradingConfig 配置的模型
  - 统一 LLM 路由层调用
  - 改进的 Prompt (含教学建议 + 错误模式识别)
"""
import json
from sqlalchemy import select
from app.db import async_session
from app.models import Essay, EssayReport, StudentAbility
from app.models.grading_config import GradingConfig, GradingProvider
from app.agents.prompts.ability_prompts import ABILITY_SUMMARY_PROMPT
from app.agents.router import call_llm


MAX_SCORES = {
    "thesis": 10,
    "content": 15,
    "language": 10,
    "structure": 5,
    "penmanship": 5,
}


async def update_student_ability(essay_id: int, teacher_id: int = 0):
    """v2.0: 教师触发能力分析更新，使用教师评分配置"""
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

        history_result = await db.execute(
            select(Essay).where(Essay.student_id == essay.student_id, Essay.status == "graded")
        )
        all_essays = history_result.scalars().all()

        ability_result = await db.execute(
            select(StudentAbility).where(StudentAbility.student_id == essay.student_id)
        )
        ability = ability_result.scalar_one_or_none()
        if not ability:
            ability = StudentAbility(student_id=essay.student_id)
            db.add(ability)

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
                if r.suggestions:
                    all_suggestions.extend(r.suggestions)
                if r.overall_comment:
                    all_comments.append(r.overall_comment)

        n = len(score_history)
        ability.overall_score = round(sum(h["total_score"] for h in score_history) / n, 1) if n > 0 else 0
        ability.essay_count = n

        for dim, mx in MAX_SCORES.items():
            scores = [h[dim] / mx * 100 for h in score_history]
            setattr(ability, f"{dim}_ability", round(sum(scores) / n, 1))

        ability.score_history = score_history

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

        ability.improvement_plan = await _build_personalized_plan_async(
            ability, score_history, all_suggestions, teacher_id=teacher_id
        )

        total_words = sum(e.word_count or 0 for e in all_essays)
        ability.vocabulary_stats = {
            "avg_word_count": round(total_words / n) if n > 0 else 0,
            "total_words": total_words,
            "essay_count": n,
        }

        ability.last_essay_id = essay_id
        await db.commit()


async def _build_personalized_plan_async(ability, history, all_suggestions, teacher_id: int = 0) -> list:
    """使用教师配置的 AI 生成个性化能力分析报告，降级到关键词匹配"""
    try:
        result = await _call_ability_ai(ability, history, all_suggestions, teacher_id=teacher_id)
        if result and len(result) >= 4:
            return result
    except Exception as e:
        print(f"[ABILITY] AI 生成失败: {e}")

    return _build_keyword_plan(ability, history, all_suggestions)


async def _call_ability_ai(ability, history, all_suggestions, teacher_id: int = 0):
    """v2.0: 使用教师 GradingConfig + 统一路由层"""

    # 读取教师评分配置
    provider = "zhipu"
    ability_model = "GLM-4-Flash-250414"
    api_key = ""
    base_url = None
    local_endpoint_url = None

    if teacher_id > 0:
        try:
            async with async_session() as db:
                config_result = await db.execute(
                    select(GradingConfig).where(GradingConfig.user_id == teacher_id)
                )
                config = config_result.scalar_one_or_none()
                if config and config.is_active:
                    provider = config.provider.value if isinstance(config.provider, GradingProvider) else config.provider
                    ability_model = config.ability_model_name or config.grading_model_name or "GLM-4-Flash-250414"
                    api_key = config.api_key_encrypted or ""
                    base_url = config.base_url
                    local_endpoint_url = config.local_endpoint_url
        except Exception as e:
            print(f"[ABILITY] 读取教师配置失败: {e}")

    if not api_key:
        from app.config import get_settings
        settings = get_settings()
        api_key = settings.AI_API_KEY or "08291980aa0d44928db4cf142733edc4.Q41wSJGtwIy2IYmc"

    # 构造分数数据
    score_lines = []
    for h in history[-5:]:
        score_lines.append(
            f"- {h['date']} 《{h['title']}》: 总分{h['total_score']}(立意{h['thesis']}/内容{h['content']}/语言{h['language']}/结构{h['structure']}/文面{h['penmanship']})"
        )
    score_data = "\n".join(score_lines) if score_lines else "暂无数据"

    seen = set()
    unique_suggestions = []
    for s in all_suggestions:
        key = s[:20]
        if key not in seen:
            seen.add(key)
            unique_suggestions.append(s)
    suggestions_text = "\n".join(f"- {s}" for s in unique_suggestions[:15])

    prompt = ABILITY_SUMMARY_PROMPT.replace("{score_data}", score_data).replace("{suggestions_text}", suggestions_text)

    result = await call_llm(
        provider=provider,
        model=ability_model,
        messages=[
            {"role": "system", "content": "你是深圳中考语文教学专家，请基于学生历史数据生成个性化能力分析，输出JSON。"},
            {"role": "user", "content": prompt},
        ],
        api_key=api_key,
        temperature=0.5,
        max_tokens=2048,
        base_url=base_url,
        local_endpoint_url=local_endpoint_url,
        timeout=60,
    )

    text = result["content"].strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]

    ai_result = json.loads(text)

    plans = []
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

    for dim in ai_result.get("dimensions", []):
        plans.append({
            "dimension": dim.get("dimension", ""),
            "level": _score_to_level(dim.get("score", 50)),
            "score": dim.get("score", 50),
            "suggestions": [dim.get("assessment", "")] + dim.get("action_items", []),
        })

    # v2.0 新增: 教学建议
    teaching = ai_result.get("teaching_recommendations", {})
    if teaching:
        teaching_items = []
        if teaching.get("immediate_week"):
            teaching_items.append(f"本周: {teaching['immediate_week']}")
        if teaching.get("short_term_2weeks"):
            teaching_items.append(f"2周: {teaching['short_term_2weeks']}")
        if teaching.get("medium_term_month"):
            teaching_items.append(f"1月: {teaching['medium_term_month']}")
        if teaching_items:
            plans.append({
                "dimension": "教学建议",
                "level": "计划",
                "score": 0,
                "suggestions": teaching_items,
            })

    # v2.0 新增: 错误模式
    error_patterns = ai_result.get("error_patterns", [])
    if error_patterns:
        error_items = [f"{ep['pattern']} (出现{ep.get('count', '?')}次, 例: {ep.get('example', '')})" for ep in error_patterns[:5]]
        if error_items:
            plans.append({
                "dimension": "共性错误",
                "level": "警告",
                "score": 0,
                "suggestions": error_items,
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
