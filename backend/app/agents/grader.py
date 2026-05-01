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

{topic_info}
## 深圳中考作文评分标准（满分 45 分，五项维度）

### 等级评定表
| 维度(满分) | 一类文 | 二类文 | 三类文 | 四类文 | 五类文 | 六类文 |
|-----------|--------|--------|--------|--------|--------|--------|
| 立意(10) | 立意深刻、角度新颖、主题鲜明、富有哲思 | 立意正确、有一定深度、角度较好 | 立意正确、有基本认识 | 立意基本正确、较浅显 | 立意模糊、认识不清 | 严重偏题、不知所云 |
| 内容(15) | 选材精当、真挚感人、详略得当、细节丰富 | 材料具体、感情真实、构思新颖 | 材料较具体、有真情实感 | 材料较空泛、细节不足 | 选材不当、内容单薄 | 内容空泛、无具体材料 |
| 语言(10) | 富有文采、表达精妙、修辞娴熟 | 生动流畅、用词准确、有表现力 | 通顺连贯、表达清楚 | 基本通顺、偶有语病 | 不够通顺、语病较多 | 文理不通、词不达意 |
| 结构(5)  | 结构严谨、首尾呼应、过渡精妙 | 结构完整、条理清晰 | 有头有尾、段落分明 | 结构基本完整 | 结构松散、条理不清 | 杂乱无章、无段落意识 |
| 文面(5)  | 卷面整洁、标点规范、无错别字 | 卷面整洁、标点正确 | 卷面较整洁 | 错误较少 | 错误较多 | 字迹潦草、错别字多 |

### 强制扣分规则（必须严格执行）
1. **完全离题**：立意0分，总分不超过 10 分，判为六类文
2. **部分偏题**：立意不超过 5 分，降两档处理
3. **字数不足 100 字**：总分不超过 10 分，判为六类文
4. **字数 100-300 字**：总分不超过 29 分
5. **字数 300-500 字**：总分不超过 34 分
6. **字数不足 600 字**：在应有等级基础上降一档
7. **出现真实校名、人名、地名**：降一档处理
8. **抄袭套作**：总分不超过 5 分，判为六类文
9. **五项分数之和必须等于 total_score**

### 评分步骤
1. 先读题目要求，判断作文是否切题（重点评估立意维度）
2. 统计字数，判断强制扣分规则是否触发
3. 逐项评定立意/内容/语言/结构/文面五个维度
4. 综合确定等级和总分
5. 验证：total_score = 立意 + 内容 + 语言 + 结构 + 文面

## 输出格式
严格输出 JSON（禁止用 ``` 包裹）：
{
  "word_count_actual": 实际字数,
  "level": "一类文/二类文/三类文/四类文/五类文/六类文",
  "topic_match": "切题/基本切题/部分偏题/完全离题",
  "total_score": 数字(必须=五项之和),
  "score_thesis": 数字(0-10),
  "score_content": 数字(0-15),
  "score_language": 数字(0-10),
  "score_structure": 数字(0-5),
  "score_penmanship": 数字(0-5),
  "deduction_reason": "扣分原因，无则填'无'",
  "basic_errors": {
    "typos": [{"text":"错字","correction":"更正","position":位置}],
    "grammar": [{"text":"病句","suggestion":"改法","position":位置}],
    "punctuation": [{"text":"标点错误","correction":"更正","position":位置}]
  },
  "paragraph_reviews": [
    {"paragraph_index":1,"original":"段落首句15字","comment":"点评","suggestion":"修改建议"}
  ],
  "overall_comment": "总体评价150-300字",
  "suggestions": ["3-5条具体建议"]
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


async def run_grader(content: str, topic_info: str = "", user_id: int = 0) -> dict:
    """执行批改。topic_info 包含作文题目、审题提示、写作要求"""

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
        return await _call_zhipu(content, topic_info, model_name, api_key)
    else:
        return await _call_openai_compatible(content, topic_info, model_name, api_key, provider)


async def _call_zhipu(content: str, topic_info: str, model: str, api_key: str) -> dict:
    """调用智谱 GLM API 批改"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    prompt = GRADER_PROMPT.replace("{topic_info}", topic_info).replace("{content}", content[:3000])

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


async def _call_openai_compatible(content: str, topic_info: str, model: str, api_key: str, provider: str) -> dict:
    """调用 OpenAI 兼容 API"""
    base_urls = {
        "openai": "https://api.openai.com/v1/chat/completions",
        "deepseek": "https://api.deepseek.com/v1/chat/completions",
    }
    url = base_urls.get(provider, "https://api.openai.com/v1/chat/completions")
    prompt = GRADER_PROMPT.replace("{topic_info}", topic_info).replace("{content}", content[:3000])

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
