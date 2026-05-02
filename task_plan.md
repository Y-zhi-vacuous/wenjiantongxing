# Task Plan: 文鉴同行 v2.0 — 实施总览

## v2.0 Goal
架构重构 — 学生端仅 OCR，评分与能力分析迁移至教师端，教师可配置多提供商（付费API/本地部署）

## v2.0 Phases

### Phase 0: 基础准备 ✅
- [x] 提取 Prompt 到独立模块 (prompts/grader_prompts.py, prompts/ability_prompts.py)
- [x] Essay 模型新增 graded_by 和 grading_requested_at 字段
- [x] grader.py 和 ability.py 导入重构

### Phase 1: 数据模型重构 ✅
- [x] 拆分 AIConfig → OCRConfig (学生) + GradingConfig (教师)
- [x] 新增 GradingProvider 枚举 (zhipu/openai/deepseek/claude/ollama/vllm)
- [x] 幂等数据迁移 (migrations.py)
- [x] 更新种子数据 (默认 OCR + Grading 配置)
- [x] main.py 集成迁移调用

### Phase 2: 后端服务/Agent 重构 ✅
- [x] 统一 LLM 路由层 call_llm() 支持 6 提供商
- [x] grader.py 使用统一路由 + 教师 GradingConfig
- [x] grading.py 接受 teacher_id + 设置 graded_by
- [x] ability.py 使用教师配置 + 统一路由
- [x] OCR 服务使用学生 OCRConfig
- [x] Prompt 优化 (切题 JSON 输出 + 能力分析教学建议)

### Phase 3: 后端 API 重构 ✅
- [x] OCR 配置 API (GET/PUT /config/ocr, POST /config/ocr/test)
- [x] 评分配置 API (GET/PUT /config/grading, POST /config/grading/test)
- [x] 教师触发单篇评分 (POST /essays/{id}/grade — 需 teacher 角色)
- [x] 未评分作文列表 (GET /essays/list/ungraded)
- [x] 一键全部评分 (POST /essays/grade-all — 串行逐篇)
- [x] 能力分析刷新 (POST /ability/refresh/{student_id})
- [x] 旧版 /config/ai 保留向后兼容

### Phase 4: 前端重构 ✅
- [x] 学生 Settings 仅 OCR 配置
- [x] 学生 WriteEssay 移除自动触发评分
- [x] 教师 Settings 完整评分配置 UI (云端API + 本地部署)
- [x] 教师 EssayView 新增「批改」按钮 + 轮询
- [x] 教师 GradingQueue 页面 (待批改列表 + 一键全部 + 单篇批改)
- [x] TypeScript 类型更新
- [x] 导航更新 (TeacherNav 增加「批改」)

## Architecture v2.0
```
React SPA (学生端: OCR配置 + 提交 / 教师端: 评分配置 + 批改)
    │ REST API
    ▼
FastAPI (Docker → GHCR → Sealos)
    ├── SQLite (prod)
    ├── OCRConfig (per student) → GLM-4V (OCR)
    ├── GradingConfig (per teacher) → call_llm → 6 providers (评分)
    └── GradingConfig (per teacher) → call_llm → 6 providers (能力分析)
```

## Decisions
| Decision | Rationale |
|----------|-----------|
| 评分迁移至教师端 | 教师可配置付费API或本地模型，更灵活 |
| 统一 call_llm 路由 | 屏蔽 6 个提供商的差异，单一接口 |
| 串行逐篇批改 | 避免并发 API 限流，单篇失败不影响其他 |
| OCR 保留学生端 | 手写识别仅影响单个学生，实时性要求高 |
| Prompt 独立模块 | 便于迭代调优，代码与 Prompt 分离 |
