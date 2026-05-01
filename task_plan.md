# Task Plan: 文鉴同行 — 实施总览

## Goal
构建 AI 作文批改系统「文鉴同行」：学生提交作文 → AI 批改 → 结构化报告 + 写作能力画像分析。支持 Web 访问 + Android APK 安装。

## Current Phase
Sealos 部署成功 ✅ — 后续：APK 构建

## Phases

### Phase 1: 项目脚手架搭建 ✅
- [x] 初始化后端项目 (FastAPI + SQLAlchemy)
- [x] 初始化前端项目 (React + Vite + TypeScript + Tailwind)
- [x] Docker Compose 编排 + .gitignore

### Phase 2: 后端核心 API ✅
- [x] 数据模型 8 张表 (User/Essay/Topic/Report/AIConfig/Class/ClassStudent/StudentAbility)
- [x] JWT 认证 (Header + Query Param)
- [x] 作文 CRUD + 文件上传 (docx/pdf/image)
- [x] GLM-4V 图片 OCR 识别
- [x] 深圳中考真题题库 (8真题+2模拟，含写作要求)
- [x] 班级管理 + 学生账号 (单个创建 + xlsx 批量导入/导出)
- [x] AI 配置 + 密码修改

### Phase 3: AI 智能体层 ✅
- [x] 智谱 GLM-4 真实 AI 批改
- [x] 异步批改 + 异常隔离
- [x] 学生能力分析 (四维画像 + 趋势 + 改进计划)

### Phase 4-5: 前端 ✅
- [x] Apple Native UI (毛玻璃/半透明/阴影)
- [x] 学生端：首页/写作/报告/历史/能力/设置
- [x] 教师端：工作台/班级/题库/作文详情/学生能力
- [x] 教师实名注册 + 学生账号教师管理
- [x] 作文原文展示 + OCR 结果展示

### Phase 6: 部署 ✅
- [x] GitHub Actions → GHCR 镜像自动构建
- [x] Sealos 部署 (公网: wppyqjhwlqso.usw-1.sealos.app)
- [x] SSH Key 永久解决 Git push
- [ ] Android APK 构建

## Architecture
```
React SPA (Web + Capacitor APK)
    │ REST API
    ▼
FastAPI (Docker → GHCR → Sealos)
    ├── SQLite (prod)
    ├── GLM-4 (批改)
    └── GLM-4V (OCR)
```

## Decisions
| Decision | Rationale |
|----------|-----------|
| GLM-4V 图片 OCR | 免装 Tesseract，手写体识别更准 |
| SSH Git push | 国内网络稳定，不受 GFW 干扰 |
| 绝对路径 DB | Sealos 容器文件系统兼容性 |
| bcrypt==4.0.1 | passlib 兼容性修复 |
