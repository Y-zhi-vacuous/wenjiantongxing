"""
能力分析 Prompt 模块 — 学生写作能力画像

v2.0 优化:
  - 纵向趋势分析: 对比近期与历史表现
  - 教学建议: 具体可执行的教学改进方案，带时间维度
  - 错误模式识别: 聚类跨作文的共性错误
"""

ABILITY_SUMMARY_PROMPT = """你是深圳中考语文教学专家。请基于以下学生的历史作文评分数据和 AI 批改建议，生成一份个性化的写作能力分析报告。

## 学生历史评分数据（按时间排列，最近在前）
{score_data}

## 学生各篇作文的 AI 批改建议汇总
{suggestions_text}

## 分析要求

### 1. 总体评估 (overall_assessment)
- 80-150字，指出最关键的写作问题和最突出的优点
- 必须包含纵向对比：与早期作文相比，哪些维度有进步/退步
- 如果有3篇以上历史作文，分析能力变化趋势

### 2. 五维分析 (dimensions)
每个维度包含：
- score: 当前能力值（0-100百分制，基于历史得分加权，近期权重大于早期）
- assessment: 15-30字的具体分析，必须引用历史数据中的具体表现
- action_items: 2-3条具体可执行的改进措施（必须是学生能直接操作的，不是空泛建议）
  格式：每条措施包含"做什么 + 怎么做 + 预期效果"

### 3. 优先改进 (priority)
- 当前最急需改进的1-2个方面（15字以内）
- 基于该生最薄弱的维度，且必须是对提分最有效的

### 4. 教学建议 (teaching_recommendations) — 给教师的建议
- immediate_week: 本周即可执行的1个课堂/课后练习（含具体操作说明）
- short_term_2weeks: 2周内可完成的专项训练计划
- medium_term_month: 1个月内系统性提升规划

### 5. 共性错误 (error_patterns) — 跨作文的错误模式识别
- 如果在多篇作文中发现相同类型错误，单独列出
- 格式: {"pattern": "错误模式描述", "count": 出现次数, "example": "典型例句"}

## 输出格式
严格输出 JSON（禁止用 ``` 包裹）：
{
  "overall_assessment": "总体评价80-150字",
  "dimensions": [
    {"dimension": "立意能力", "score": 数字(0-100), "assessment": "具体分析15-30字", "action_items": ["具体可执行的改进措施1", "措施2", "措施3"]},
    {"dimension": "内容能力", "score": 数字(0-100), "assessment": "...", "action_items": ["..."]},
    {"dimension": "语言能力", "score": 数字(0-100), "assessment": "...", "action_items": ["..."]},
    {"dimension": "结构能力", "score": 数字(0-100), "assessment": "...", "action_items": ["..."]},
    {"dimension": "文面能力", "score": 数字(0-100), "assessment": "...", "action_items": ["..."]}
  ],
  "priority": "当前最急需改进的1-2个方面（15字以内）",
  "teaching_recommendations": {
    "immediate_week": "本周课堂/课后练习方案（15-30字）",
    "short_term_2weeks": "2周专项训练计划（15-30字）",
    "medium_term_month": "1个月系统提升规划（15-30字）"
  },
  "error_patterns": [
    {"pattern": "共性错误描述", "count": 出现次数, "example": "典型例句片段"}
  ]
}"""
