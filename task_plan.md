# Task Plan: 文鉴同行 v2.1

## 当前状态
v2.1 — 深圳市官方四维评分标准。公网 `wppyqjhwlqso.usw-1.sealos.app`

## v2.0 完成事项 ✅
- 学生端 OCR / 教师端评分能力分离
- 统一 LLM 路由层 (6 providers)
- 教师一键批改 (串行逐篇)
- API Key 独立配置 (评分/能力可不同提供商)
- 默认模型勾选框
- 切题判定报告展示 (topic_match/level/deduction_reason)
- Prompt 独立模块化
- 幂等数据迁移

## v2.1 完成事项 ✅
- 深圳市官方四维评分标准: 内容(15,含立意) + 语言(15) + 结构(10) + 文面(5) = 45
- 审题判断修正: 看核心思想方向而非描写篇幅占比
- Prompt 重写: 角色定位 + 官方评分表 + 评分原则 + 评分流程
- 偏题/离题硬限更新: 内容≤6/总分≤25(偏题), 内容≤3/总分≤10(离题)
- 前端适配四维度展示
- 能力分析适配四维度

## Architecture v2.1
```
React SPA (学生: OCR配置+提交 / 教师: 评分配置+批改)
    │ REST API
    ▼
FastAPI (Docker → GHCR → Sealos)
    ├── SQLite
    ├── OCRConfig (per student) → GLM-4V
    ├── GradingConfig (per teacher) → call_llm → 6 providers (评分)
    └── GradingConfig (per teacher) → call_llm → 6 providers (能力)
```
