"""
批改 Agent — 支持智谱 GLM API 和 Mock 模式
"""

import json
import httpx
from sqlalchemy import select
from app.db import async_session
from app.models.ai_config import AIConfig

GRADER_PROMPT = """你是一位资深的深圳中考语文阅卷老师。请严格按以下标准批改学生作文。

## 深圳中考作文评分标准
- 满分 45 分（含书写分 3 分）
- 内容 (40%，约 18 分)：审题是否准确、立意是否深刻、素材是否充实
- 语言 (30%，约 13 分)：表达是否流畅、修辞是否得当、是否有文采
- 结构 (20%，约 9 分)：开头结尾是否呼应、段落清晰度、过渡自然度
- 卷面 (10%，约 5 分)：分段合理、字数达标（600-900字）、用语规范

## 输出要求
请严格输出 JSON 格式（不要包含 markdown 代码块标记），结构如下：
{
  "total_score": 数字(满分45),
  "score_content": 数字(满分约18),
  "score_language": 数字(满分约13),
  "score_structure": 数字(满分约9),
  "score_penmanship": 数字(满分约5),
  "basic_errors": {
    "typos": [{"text": "错字原文", "correction": "正确写法", "position": 位置}],
    "grammar": [{"text": "病句原文", "suggestion": "修改建议", "position": 位置}],
    "punctuation": [{"text": "标点错误", "correction": "正确标点", "position": 位置}]
  },
  "paragraph_reviews": [
    {"paragraph_index": 1, "original": "段落原文(前30字)", "comment": "点评(50-100字)", "suggestion": "具体修改建议(可选)"}
  ],
  "overall_comment": "总体评价(150-300字)，包含优点和不足，语气鼓励为主",
  "suggestions": ["3-5条具体可行的提升建议，每条20-50字"]
}

## 学生作文
{content}

请批改："""

MOCK_REPORT = {
    "total_score": 42,
    "score_content": 17,
    "score_language": 12,
    "score_structure": 8,
    "score_penmanship": 5,
    "basic_errors": {
        "typos": [{"text": "己经", "correction": "已经", "position": 45}],
        "grammar": [{"text": "通过这次经历，使我明白了坚持的意义。", "suggestion": "改为：这次经历使我明白了坚持的意义。", "position": 120}],
        "punctuation": [{"text": "。。。", "correction": "……", "position": 300}],
    },
    "paragraph_reviews": [
        {"paragraph_index": 1, "original": "今天天气很好，我和同学一起去爬山...",
         "comment": "开头过于平淡，建议用场景描写或悬念引入。深圳中考阅卷中，开头质量直接影响基础等级评定。",
         "suggestion": "用具体场景或感受开头，如'汗水模糊了视线的那一刻...'"},
        {"paragraph_index": 2, "original": "到了山顶，我们都很开心。",
         "comment": "情感表达空泛，'开心'太笼统。中考作文要求真情实感，需要有具体的细节支撑。",
         "suggestion": "用具体的动作、心理活动或感官细节来替代概括性的情感词。"},
    ],
    "overall_comment": "本文选材生活化，叙事完整，但立意深度不足。主要问题：1) 开头缺乏吸引力，落入'今天天气很好'的套路；2) 细节描写不够，多为概括性叙述，缺少画面感；3) 结尾缺少升华，未能将个人经历与更大的主题联系起来。建议多读优秀记叙文，注重学习'以小见大'的写法。",
    "suggestions": [
        "动笔前用一句话写出文章核心立意，确保全文围绕立意展开",
        "每个场景至少用2个感官细节（看/听/触/嗅）来描写",
        "结尾尝试联系更大的主题（成长/亲情/社会），让文章有余味",
    ],
    "model_used": "mock",
}


async def run_grader(content: str, user_id: int = 0) -> dict:
    """执行批改。优先使用用户配置的 AI，否则使用默认智谱 API"""

    # 读取配置：环境变量 → 用户配置 → 默认
    from app.config import get_settings
    settings = get_settings()
    provider = settings.AI_PROVIDER or "zhipu"
    model_name = settings.AI_MODEL or "glm-4-flash"
    api_key = settings.AI_API_KEY or ""

    if user_id > 0:
        try:
            async with async_session() as db:
                result = await db.execute(select(AIConfig).where(AIConfig.user_id == user_id))
                config = result.scalar_one_or_none()
                if config and config.api_key_encrypted:
                    provider = config.provider
                    model_name = config.model_name
                    api_key = config.api_key_encrypted
        except Exception:
            pass

    if provider == "zhipu":
        return await _call_zhipu(content, model_name, api_key)
    else:
        return await _call_openai_compatible(content, model_name, api_key, provider)


async def _call_zhipu(content: str, model: str, api_key: str) -> dict:
    """调用智谱 GLM API"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    prompt = GRADER_PROMPT.replace("{content}", content[:3000])

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json={
            "model": model,
            "messages": [
                {"role": "system", "content": "你是深圳中考语文阅卷老师，请严格按JSON格式输出批改结果。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 4096,
        }, headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })
        data = resp.json()

        if "choices" not in data:
            print(f"[Zhipu Error] {data}")
            return MOCK_REPORT

        text = data["choices"][0]["message"]["content"]
        return _parse_ai_response(text, model)


async def _call_openai_compatible(content: str, model: str, api_key: str, provider: str) -> dict:
    """调用 OpenAI 兼容 API"""
    base_urls = {
        "openai": "https://api.openai.com/v1/chat/completions",
        "deepseek": "https://api.deepseek.com/v1/chat/completions",
        "claude": "https://api.anthropic.com/v1/messages",
    }
    url = base_urls.get(provider, "https://api.openai.com/v1/chat/completions")
    prompt = GRADER_PROMPT.replace("{content}", content[:3000])

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json={
            "model": model,
            "messages": [
                {"role": "system", "content": "你是深圳中考语文阅卷老师，请严格按JSON格式输出批改结果。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 4096,
        }, headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })
        data = resp.json()

        if "choices" not in data:
            return MOCK_REPORT

        text = data["choices"][0]["message"]["content"]
        return _parse_ai_response(text, model)


def _parse_ai_response(text: str, model: str) -> dict:
    """解析 AI 返回的 JSON"""
    # 去除可能的 markdown 代码块标记
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
        # 尝试提取 JSON 内容
        import re
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                result = json.loads(match.group())
                result["model_used"] = model
                return result
            except json.JSONDecodeError:
                pass
        return MOCK_REPORT
