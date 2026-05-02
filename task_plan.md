# Task Plan: 文鉴同行 v2.1

## 当前状态
v2.1 — 深圳市官方四维评分标准，能力画像 100 分制，APK 已构建。公网 `wppyqjhwlqso.usw-1.sealos.app`

## v2.0 完成 ✅
- 学生/教师分离，OCR 学生端 + 评分能力教师端
- 统一 LLM 路由 (6 providers)
- 教师一键批改 (串行逐篇)
- API Key 独立配置 (评分/能力可不同提供商)
- 默认模型勾选框
- 切题判定报告展示 (topic_match/level/deduction_reason)
- Prompt 独立模块化 + 幂等数据迁移

## v2.1 完成 ✅
- 深圳市官方四维标准: 内容15+语言15+结构10+文面5=45
- 审题判断修正: 看核心思想方向而非描写篇幅占比
- Prompt 重写: 角色定位+官方评分表+评分原则
- 教师重新批改: 覆盖旧报告，重新 AI 评分
- 学生评分反馈: 留言评价 → 同步教师端 (essay_feedback 表)
- 能力画像 100 分制: 综合均分/四维能力值百分制
- 能力 AI 使用系统计算分数 (不自行编造)
- 前端 4 维度适配 + 图表修复
- APK v2.1 构建

## Architecture
```
React SPA (学生: OCR+反馈 / 教师: 评分配置+批改+反馈查看)
    │ REST API
    ▼
FastAPI (Docker → GHCR → Sealos)
    ├── SQLite (10 tables)
    ├── OCRConfig → GLM-4V
    ├── GradingConfig → call_llm → 6 providers (评分+能力)
    └── EssayFeedback (学生留言)

Android APK (Capacitor 8)
```
