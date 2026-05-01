"""
批改 Agent — 深圳中考六类文评分标准
支持智谱 GLM API 和 Mock 模式
"""

import json
import httpx
from sqlalchemy import select
from app.db import async_session
from app.models.ai_config import AIConfig

GRADER_PROMPT = """你是一位资深的深圳中考语文阅卷老师。请严格按照以下标准批改学生作文。

## 深圳中考作文评分标准（满分 45 分）

### 等级评定表
| 项目 | 一类文 | 二类文 | 三类文 | 四类文 | 五类文 | 六类文 |
|------|--------|--------|--------|--------|--------|--------|
| 分数范围 | 45 | 40-44 | 35-39 | 30-34 | 25-29 | 0-24 |
| 内容 | 富有创意、真挚感人、内容丰富、构思巧妙、详略得当 | 立意正确、感情真挚、材料具体、构思新颖、详略得当 | 立意正确、融入情感、材料具体、有详有略 | 立意基本正确、材料较具体 | 立意不正确、选材不恰当 | 严重偏题、内容空泛 |
| 语言 | 富有文采 | 生动流畅 | 通顺连贯、较生动 | 基本连贯、有一些语病 | 不够通顺、语病较多 | 文理不通 |
| 结构 | 严谨 | 严谨 | 完整有条理 | 结构基本完整、条理基本清楚 | 结构不完整、条理不清楚 | 杂乱无章 |
| 文面 | 卷面整洁、标点正确 | 卷面整洁、标点正确 | 卷面较整洁、标点正确 | 写字标点错误较少 | 写字标点错误较多 | 字迹潦草、标点不清、错别字较多 |

### 强制扣分规则（必须严格执行）
1. **字数不足 100 字**：直接判为六类文，总分不超过 10 分
2. **字数 100-300 字**：最高不超过五类文（29 分）
3. **字数 300-500 字**：最高不超过四类文（34 分）
4. **字数不足 600 字**：在应有等级基础上降一档
5. **完全离题**：直接判为六类文，总分不超过 10 分
6. **部分偏题**：降两档处理
7. **出现真实校名、人名、地名**：降一档处理
8. **抄袭套作**：直接判为六类文，总分不超过 5 分
9. **仅有一段文字、无段落结构**：结构分不超过 3 分
10. **四者分数之和必须等于 total_score**，不允许四者之和与总分不一致

### 评分步骤
第一步：统计字数，判断是否符合强制扣分规则
第二步：逐项评定内容/语言/结构/文面等级
第三步：综合评定最终等级和总分
第四步：确保总分 = 内容分 + 语言分 + 结构分 + 文面分

## 输出格式
请严格输出 JSON（不要包含 ``` 代码块标记）：
{
  "word_count_actual": 实际统计的字数,
  "level": "一类文/二类文/三类文/四类文/五类文/六类文",
  "total_score": 数字(总分=四项之和),
  "score_content": 数字,
  "score_language": 数字,
  "score_structure": 数字,
  "score_penmanship": 数字,
  "deduction_reason": "扣分原因简述，如无扣分则填'无'",
  "basic_errors": {
    "typos": [{"text": "错字", "correction": "更正", "position": 位置}],
    "grammar": [{"text": "病句", "suggestion": "修改建议", "position": 位置}],
    "punctuation": [{"text": "标点错误", "correction": "更正", "position": 位置}]
  },
  "paragraph_reviews": [
    {"paragraph_index": 1, "original": "段落首句", "comment": "具体点评", "suggestion": "修改建议"}
  ],
  "overall_comment": "总体评价150-300字，先优点后不足，以鼓励收尾",
  "suggestions": ["3-5条具体可行的提升建议"]
}

## 学生作文
{content}

请批改："""

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


async def run_grader(content: str, user_id: int = 0) -> dict:
    """执行批改。优先使用用户配置的评分模型，默认 GLM-4-Flash-250414"""

    from app.config import get_settings
    settings = get_settings()

    # 优先读取用户配置，否则用系统默认
    provider = settings.AI_PROVIDER or "zhipu"
    model_name = settings.AI_GRADING_MODEL or "GLM-4-Flash-250414"
    api_key = settings.AI_API_KEY or "08291980aa0d44928db4cf142733edc4.Q41wSJGtwIy2IYmc"

    if user_id > 0:
        try:
            async with async_session() as db:
                result = await db.execute(select(AIConfig).where(AIConfig.user_id == user_id))
                config = result.scalar_one_or_none()
                if config and config.api_key_encrypted:
                    provider = config.provider
                    model_name = config.grading_model_name or "GLM-4-Flash-250414"
                    api_key = config.api_key_encrypted
        except Exception:
            pass

    if provider == "zhipu":
        return await _call_zhipu(content, model_name, api_key)
    else:
        return await _call_openai_compatible(content, model_name, api_key, provider)


async def _call_zhipu(content: str, model: str, api_key: str) -> dict:
    """调用智谱 GLM API 批改"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    prompt = GRADER_PROMPT.replace("{content}", content[:3000])

    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(url, json={
            "model": model,
            "messages": [
                {"role": "system", "content": "你是深圳中考语文阅卷老师，请严格按照深圳中考六类文评分标准批改，输出JSON格式结果。"},
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
    }
    url = base_urls.get(provider, "https://api.openai.com/v1/chat/completions")
    prompt = GRADER_PROMPT.replace("{content}", content[:3000])

    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(url, json={
            "model": model,
            "messages": [
                {"role": "system", "content": "你是深圳中考语文阅卷老师，请严格按照深圳中考六类文评分标准批改，输出JSON格式结果。"},
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
        return MOCK_REPORT
