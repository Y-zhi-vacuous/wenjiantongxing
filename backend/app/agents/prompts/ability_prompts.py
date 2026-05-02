"""
能力分析 Prompt 模块 — 学生写作能力画像

v2.1:
  - 传入系统实际计算的能力分数，AI 基于真实数据做分析（不自拟分数）
  - 纵向趋势 + 教学建议 + 错误模式识别
"""

ABILITY_SUMMARY_PROMPT = """你是深圳中考语文教学专家。请基于以下学生的真实历史数据，生成一份个性化的写作能力分析报告。

## 学生当前能力值（系统计算，请基于此数据做分析）
{ability_scores}

## 学生历史评分数据（按时间排列，最近在前）
{score_data}

## 学生各篇作文的 AI 批改建议汇总
{suggestions_text}

## 重要：评分一致性要求
- dimensions 中的 score 必须使用上面「当前能力值」中系统计算的实际分数，不要自己编
- 你的任务是基于这些真实分数，给出专业的 assessment 分析和 action_items 改进措施

## 分析要求

### 1. 总体评估 (overall_assessment)
- 80-150字，基于真实能力值指出最关键问题和最突出优点
- 必须包含纵向对比：近期 vs 早期作文的进退步
- 3篇以上历史作文 → 必须分析能力变化趋势

### 2. 四维分析 (dimensions)
每个维度：
- score: 使用系统提供的实际能力值
- assessment: 15-30字，结合历史数据中的具体表现进行分析
- action_items: 2-3条具体可执行的改进措施

### 3. 优先改进 (priority)
- 基于最薄弱的维度，指明对提分最有效的1-2个方面（15字以内）

### 4. 教学建议 (teaching_recommendations)
- immediate_week: 本周可执行的课堂/课后练习
- short_term_2weeks: 2周专项训练计划
- medium_term_month: 1个月系统提升规划

### 5. 共性错误 (error_patterns)
- 跨作文的相同类型错误，含出现次数和典型例句

## 输出格式
严格输出 JSON（禁止用 ``` 包裹）：
{
  "overall_assessment": "总体评价80-150字",
  "dimensions": [
    {"dimension": "内容能力", "score": 使用系统提供的实际值, "assessment": "15-30字", "action_items": ["措施1", "措施2"]},
    {"dimension": "语言能力", "score": 使用系统提供的实际值, "assessment": "...", "action_items": ["..."]},
    {"dimension": "结构能力", "score": 使用系统提供的实际值, "assessment": "...", "action_items": ["..."]},
    {"dimension": "文面能力", "score": 使用系统提供的实际值, "assessment": "...", "action_items": ["..."]}
  ],
  "priority": "最急需改进的1-2个方面（15字以内）",
  "teaching_recommendations": {
    "immediate_week": "本周练习方案",
    "short_term_2weeks": "2周训练计划",
    "medium_term_month": "1月提升规划"
  },
  "error_patterns": [
    {"pattern": "错误模式", "count": 次数, "example": "例句"}
  ]
}"""
