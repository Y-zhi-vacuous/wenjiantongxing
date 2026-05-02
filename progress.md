# Progress Log

## 2026-05-02: v2.0 架构重构

### Phase 0: 基础准备 ✅
Prompt 模块化 · graded_by 字段

### Phase 1: 数据模型 ✅
OCRConfig/GradingConfig 拆分 · 迁移 · 种子数据

### Phase 2: 服务层 ✅
统一 LLM 路由 (call_llm, 6 providers) · grader 重构 · ability 重构 · OCR 学生配置 · Prompt 优化

### Phase 3: API ✅
OCR 配置 API · 评分配置 API · 教师触发评分 · 未评分列表 · 一键全部 · 能力刷新

### Phase 4: 前端 ✅
学生 Settings(OCR only) · WriteEssay(去自动批改) · 教师 Settings(评分配置UI) · EssayView(批改按钮) · GradingQueue(待批改列表+一键全部) · 导航更新

---

## 2026-04-30 ~ 2026-05-02: v1.0

### 设计 ✅
需求澄清 → FastAPI+React → Apple UI 打样

### 后端 ✅
8 模型 + JWT + CRUD + 文件解析 + GLM-4 批改 + OCR + xlsx + 密码修改

### 前端 ✅
学生 8 页 + 教师 7 页 + Apple UI + 原文展示

### AI 优化 ✅
五维评分 + 切题硬限 + Prompt 审题第一步 + OCR 容错链 + 能力 AI 驱动

### 部署 ✅
Actions → GHCR → Sealos + SSH Git + APK v1.0

## 测试
全部通过: Health/Login/Topics/Essay+Grade/OCR/Ability/xlsx/Build/Docker/APK/Sealos
