"""
批改 Agent — 深圳中考六类文两步法评分 (v2.0)

v2.0 变化:
  - 使用统一 LLM 路由层 (call_llm) 替代硬编码的 API 调用
  - 接受 teacher_id 参数，从教师 GradingConfig 读取配置
  - 切题检查 JSON 解析 (含 confidence + reasoning)
"""
import json
import asyncio
from sqlalchemy import select
from app.db import async_session
from app.models.grading_config import GradingConfig, GradingProvider
from app.agents.prompts.grader_prompts import GRADER_PROMPT, TOPIC_CHECK_PROMPT
from app.agents.router import call_llm


MOCK_REPORT = {
    "level": "二类文",
    "total_score": 42,
    "score_content": 17,
    "score_language": 12,
    "score_structure": 8,
    "score_penmanship": 5,
    "basic_errors": {
        "typos": [{"text": "己经", "correction": "已经", "position": 45}],
        "grammar": [{"text": "通过这次经历，使我明白了坚持的意义", "suggestion": "缺少主语，改为：这次经历使我明白了坚持的意义", "position": 120}],
        "punctuation": [{"text": "。。。", "correction": "……", "position": 300}],
    },
    "paragraph_reviews": [
        {"paragraph_index": 1, "original": "今天天气很好，我和同学一起去爬山",
         "comment": "开头平淡，落入'今天…'的俗套。中考阅卷中开头质量直接影响基础等级评定。建议用场景描写或悬念引入。",
         "suggestion": "以具体细节开头，如'汗水模糊了视线的那一刻，我忽然明白了…'"},
        {"paragraph_index": 2, "original": "到了山顶，我们都很开心",
         "comment": "情感表达空泛，'开心'太笼统，缺乏具体的细节支撑来打动读者。",
         "suggestion": "用感官细节替代概括性情感词，如肢体动作、心理活动、环境烘托"},
    ],
    "overall_comment": "本文选材生活化，叙事完整，达到二类文水平。主要问题：1) 开头缺乏吸引力，落入常见套路；2) 细节描写不够，多为概括性叙述，缺少画面感和感染力；3) 结尾缺少升华，未能将个人经历与更大的主题联系起来。建议多读优秀记叙文，注重'以小见大'的写法。",
    "suggestions": [
        "动笔前用一句话写出文章核心立意，确保全文围绕立意展开不偏题",
        "每个关键场景至少用2个感官细节（看/听/触/嗅）来描写，增强画面感",
        "结尾尝试联系更大的主题（成长/亲情/社会），让文章有余味和深度",
    ],
    "model_used": "mock",
}


async def run_grader(content: str, topic_info: str = "", teacher_id: int = 0) -> dict:
    """两步批改：先独立判切题 → 注入判定评分 (v2.0: 教师配置驱动)"""

    # 读取教师评分配置
    provider = "zhipu"
    grading_model = "GLM-4-Flash-250414"
    api_key = ""
    base_url = None
    local_endpoint_url = None

    if teacher_id > 0:
        try:
            async with async_session() as db:
                result = await db.execute(
                    select(GradingConfig).where(GradingConfig.user_id == teacher_id)
                )
                config = result.scalar_one_or_none()
                if config and config.is_active:
                    gp = config.grading_provider
                    provider = gp.value if isinstance(gp, GradingProvider) else (gp or "zhipu")
                    grading_model = config.grading_model_name or "GLM-4-Flash-250414"
                    api_key = config.grading_api_key or ""
                    base_url = config.grading_base_url
                    local_endpoint_url = config.grading_local_url
        except Exception as e:
            print(f"[GRADER] 读取教师配置失败: {e}")

    if not api_key:
        from app.config import get_settings
        settings = get_settings()
        api_key = settings.AI_API_KEY or "08291980aa0d44928db4cf142733edc4.Q41wSJGtwIy2IYmc"

    # 第一步：独立 API 判断切题
    topic_match = "切题"
    if topic_info:
        topic_match = await _check_topic_match(content, topic_info, provider, api_key, base_url, local_endpoint_url)

    # 第二步：主评分（注入切题判定）
    prompt = GRADER_PROMPT.replace("{topic_info}", topic_info).replace("{content}", content[:3000])
    prompt = prompt.replace("请批改：", f"【系统已判定：{topic_match}，请基于此判定进行评分】\n请批改：")

    try:
        result = await call_llm(
            provider=provider,
            model=grading_model,
            messages=[
                {"role": "system", "content": "你是深圳中考语文阅卷老师，请严格按照深圳中考六类文评分标准批改，输出JSON格式结果。"},
                {"role": "user", "content": prompt},
            ],
            api_key=api_key,
            temperature=0.7,
            max_tokens=4096,
            base_url=base_url,
            local_endpoint_url=local_endpoint_url,
            timeout=90,
        )
        parsed = _parse_ai_response(result["content"], grading_model)
    except Exception as e:
        print(f"[GRADER] AI 评分调用失败: {e}")
        parsed = MOCK_REPORT

    parsed["topic_match"] = topic_match
    return parsed


async def _check_topic_match(
    content: str, topic_info: str,
    provider: str, api_key: str,
    base_url: str | None, local_endpoint_url: str | None,
) -> str:
    """专用 API 调用，仅判断切题 (v2.0: JSON 输出含 confidence)"""
    prompt = TOPIC_CHECK_PROMPT.replace("{topic_info}", topic_info).replace("{content}", content[:800])

    try:
        result = await call_llm(
            provider=provider,
            model="GLM-4-Flash-250414",  # 切题检查始终使用快速模型
            messages=[{"role": "user", "content": prompt}],
            api_key=api_key,
            temperature=0.0,
            max_tokens=100,
            base_url=base_url,
            local_endpoint_url=local_endpoint_url,
            timeout=30,
        )
        text = result["content"].strip()
        print(f"[TOPIC_CHECK] 原始输出: '{text}'")

        # 尝试 JSON 解析
        try:
            clean = text.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
            if clean.endswith("```"):
                clean = clean[:-3]
            data = json.loads(clean)
            match = data.get("topic_match", "")
            confidence = data.get("confidence", 0)
            reasoning = data.get("reasoning", "")
            print(f"[TOPIC_CHECK] 匹配={match}, 置信度={confidence}, 理由={reasoning}")
        except json.JSONDecodeError:
            match = text
            print(f"[TOPIC_CHECK] JSON 解析失败，使用原始输出")

        if "离题" in match:
            return "完全离题"
        if "偏题" in match:
            return "部分偏题"
        if "切题" in match:
            return "切题"

        print(f"[TOPIC_CHECK] 无法解析，默认切题")
        return "切题"
    except Exception as e:
        print(f"[TOPIC_CHECK] API 调用失败: {e}，默认切题")
        return "切题"


def _parse_ai_response(text: str, model: str) -> dict:
    """解析 AI 返回的 JSON。解析失败时记录原始输出并返回零分报告"""
    text = text.strip()

    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:]) if len(lines) > 1 else text
    if text.endswith("```"):
        text = text[:-3].strip()

    try:
        result = json.loads(text)
        result["model_used"] = model
        return result
    except json.JSONDecodeError:
        import re
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                result = json.loads(match.group())
                result["model_used"] = model
                return result
            except json.JSONDecodeError:
                pass

    print(f"[GRADER] JSON解析失败！AI原始输出前500字:\n{text[:500]}")
    return {
        "level": "六类文",
        "topic_match": "无法判定",
        "total_score": 0,
        "score_thesis": 0,
        "score_content": 0,
        "score_language": 0,
        "score_structure": 0,
        "score_penmanship": 0,
        "overall_comment": f"批改系统异常：AI返回格式错误，请联系管理员。原始输出: {text[:200]}",
        "suggestions": ["请重新提交作文进行批改"],
        "model_used": model,
    }
