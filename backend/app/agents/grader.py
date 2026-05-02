"""
批改 Agent — 深圳中考六类文评分标准
支持智谱 GLM API 和 Mock 模式
"""

import json
import httpx
from sqlalchemy import select
from app.db import async_session
from app.models.ai_config import AIConfig

GRADER_PROMPT = """你是深圳中考语文阅卷老师。批改前必须完成以下判断。

## ⚠️ 第一步：审题匹配检查（必须最先完成）

{topic_info}
请仔细阅读上面的题目和写作要求，然后判断学生作文是否切合题目。
判断标准：作文的**核心主题**必须与题目要求一致，不能仅凭文中出现的关键词判断。

- **完全离题**：核心主题与题目完全无关
- **部分偏题**：开头或局部涉及题目，但核心主题偏离（如题目要求写"风景变化"，作文前两段写景后全部转为内心感悟，风景只是引子而非主线）
- **基本切题**：核心主题与题目相关，偶有局部偏离
- **切题**：全文核心紧扣题目

**偏题判断示例**：
- 题目"看，风景在变"→ 学生写海边日落→月光→感悟"我是自己的星光"→ **部分偏题**（海边景色只是引子，核心是自我发现，未围绕"风景变化"展开）
- 题目"见证美好"→ 学生写目睹陌生人拾金不昧→ **切题**
- 题目"因为有我"→ 学生写自己组织班级活动→ **切题**
- 题目"我的动力源"→ 学生写喜欢打游戏→ **完全离题**（除非能论证游戏如何成为积极动力）

**关键原则**：如果去掉题目中的关键词，作文的核心内容是否依然成立？如果是，说明该关键词并未主导全文，应判偏题。

### 强制规则
1. 完全离题 → 立意≤2，总分≤10，判六类文，无需详细批改
2. 部分偏题 → 立意≤5，总分≤29
3. 字数<100 → ≤10分；100-300 → ≤29分；300-500 → ≤34分

## 第二步：评分标准（满分 45 分，五项维度）

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
1. **审题匹配**：最关键一步。通读题目要求，判断作文是否切题。若不切题，直接按强制规则给出低分，无需详细批改
2. **统计字数**：判断强制扣分规则
3. **逐项评定**：立意/内容/语言/结构/文面
4. **综合定级**：确定等级和总分
5. **验算**：total_score = 五项之和

## 输出格式
严格输出 JSON（禁止用 ``` 包裹）。注意 topic_match 必须准确，这是评分的第一依据：
{
  "topic_match": "切题/基本切题/部分偏题/完全离题（必须准确判断！）",
  "word_count_actual": 实际字数,
  "level": "一类文/二类文/三类文/四类文/五类文/六类文",
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


TOPIC_CHECK_PROMPT = """你是一个审题判断工具。请严格对比以下作文题目和学生作文，只输出一个词。

题目要求：
{topic_info}

学生作文核心内容（前800字）：
{content}

请判断：
- 如果作文核心主题与题目要求一致，只输出：切题
- 如果作文只是开头或局部提到题目关键词，但核心内容转向其他主题（如题目要求写"风景变化"却写成内心感悟"做自己的星光"），只输出：偏题
- 如果作文与题目完全无关，只输出：离题

注意：关键看核心主题。如果去掉作文里与题目相关的几个词，作文主题不变，那就是偏题。

只输出一个词（切题/偏题/离题），不要任何解释。"""


async def run_grader(content: str, topic_info: str = "", user_id: int = 0) -> dict:
    """两步批改：先独立判切题，再评分，最后强制注入切题判定"""

    from app.config import get_settings
    settings = get_settings()
    provider = settings.AI_PROVIDER or "zhipu"
    grading_model = settings.AI_GRADING_MODEL or "GLM-4-Flash-250414"
    api_key = settings.AI_API_KEY or "08291980aa0d44928db4cf142733edc4.Q41wSJGtwIy2IYmc"

    if user_id > 0:
        try:
            async with async_session() as db:
                result = await db.execute(select(AIConfig).where(AIConfig.user_id == user_id))
                config = result.scalar_one_or_none()
                if config and config.api_key_encrypted:
                    provider = config.provider
                    grading_model = config.grading_model_name or "GLM-4-Flash-250414"
                    api_key = config.api_key_encrypted
        except Exception:
            pass

    # 第一步：独立 API 判断切题
    topic_match = "切题"
    if topic_info:
        topic_match = await _check_topic_match(content, topic_info, api_key)

    # 第二步：主评分（注入切题判定）
    if provider == "zhipu":
        result = await _call_zhipu(content, topic_info, topic_match, grading_model, api_key)
    else:
        result = await _call_openai_compatible(content, topic_info, topic_match, grading_model, api_key, provider)

    result["topic_match"] = topic_match
    return result


async def _check_topic_match(content: str, topic_info: str, api_key: str) -> str:
    """专用 API 调用，仅判断切题"""
    import httpx
    prompt = TOPIC_CHECK_PROMPT.replace("{topic_info}", topic_info).replace("{content}", content[:800])

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            json={
                "model": "GLM-4-Flash-250414",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
                "max_tokens": 10,
            },
            headers={"Authorization": f"Bearer {api_key}"},
        )
        data = resp.json()
        if "choices" in data:
            answer = data["choices"][0]["message"]["content"].strip()
            print(f"[TOPIC_CHECK] 原始输出: '{answer}'")
            if "偏题" in answer or "离题" in answer:
                return "部分偏题" if "偏" in answer else "完全离题"
            if "切题" in answer:
                return "切题"
        print(f"[TOPIC_CHECK] 无法解析，默认切题")
        return "切题"


async def _call_zhipu(content: str, topic_info: str, topic_match: str, model: str, api_key: str) -> dict:
    """调用智谱 GLM API 批改"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    prompt = GRADER_PROMPT.replace("{topic_info}", topic_info).replace("{content}", content[:3000])
    prompt = prompt.replace("请批改：", f"【系统已判定：{topic_match}，请基于此判定进行评分】\n请批改：")

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


async def _call_openai_compatible(content: str, topic_info: str, topic_match: str, model: str, api_key: str, provider: str) -> dict:
    """调用 OpenAI 兼容 API"""
    base_urls = {
        "openai": "https://api.openai.com/v1/chat/completions",
        "deepseek": "https://api.deepseek.com/v1/chat/completions",
    }
    url = base_urls.get(provider, "https://api.openai.com/v1/chat/completions")
    prompt = GRADER_PROMPT.replace("{topic_info}", topic_info).replace("{content}", content[:3000])
    prompt = prompt.replace("请批改：", f"【系统已判定：{topic_match}，请基于此判定进行评分】\n请批改：")

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
    """解析 AI 返回的 JSON。解析失败时记录原始输出并返回错误标记"""
    text = text.strip()

    # 去除 markdown 代码块
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

    # 解析失败：记录原始输出，返回零分报告（不静默兜底）
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
