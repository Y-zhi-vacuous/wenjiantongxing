# Task Plan: 文鉴同行 — 实施总览

## Goal
构建 AI 作文批改系统「文鉴同行」：学生提交作文 → AI 批改 → 结构化报告 + 写作能力画像分析。支持 Web 访问 + Android APK 安装。

## Current Phase
Sealos 部署调试中

## Phases

### Phase 1: 项目脚手架搭建 ✅
- [x] 初始化后端项目 (FastAPI + SQLAlchemy)
- [x] 初始化前端项目 (React + Vite + TypeScript + Tailwind)
- [x] Docker Compose 编排 PostgreSQL / Redis / MinIO
- [x] CORS、环境变量、.gitignore

### Phase 2: 后端核心 API ✅
- [x] SQLAlchemy 数据模型 (8 张表含 StudentAbility)
- [x] JWT 认证 (Header + Query Param 双模式)
- [x] 作文 CRUD + 文件上传 (docx/pdf/image)
- [x] 深圳中考真题题库 (8真题+2模拟，含写作要求)
- [x] 班级管理 + 学生账号 (单个创建 + xlsx 批量导入/导出)
- [x] AI 配置 + 学生密码修改

### Phase 3: AI 智能体层 ✅
- [x] 智谱 GLM-4 真实 AI 批改
- [x] Mock Agent 开发模式
- [x] 异步批改 + 异常隔离
- [x] 学生能力分析 (四维能力画像 + 趋势 + 改进计划)

### Phase 4-5: 前端 ✅
- [x] Apple Native 风格 UI (毛玻璃/半透明/阴影)
- [x] 学生端 8 页 (登录/首页/写作/报告/历史/能力/设置)
- [x] 教师端 6 页 (工作台/班级/题库/作文查看/设置)
- [x] 教师实名注册 + 学生账号教师管理

### Phase 6: 部署 ✅
- [x] GitHub Actions 自动构建 Docker 镜像
- [x] GHCR 镜像仓库: `ghcr.io/y-zhi-vacuous/wenjiantongxing:latest`
- [x] Capacitor Android 项目初始化
- [ ] Sealos 部署完成 (当前: 503 调试中)
- [ ] APK 构建

## Architecture
```
React SPA (Web + Capacitor APK)
    │ REST API
    ▼
FastAPI (Docker → GHCR → Sealos)
    │
    ▼
SQLite (dev) / PostgreSQL (prod)
    │
    ▼
智谱 GLM-4 (AI 批改)
```

## Decisions
| Decision | Rationale |
|----------|-----------|
| SQLite 生产环境 | 零配置，Sealos 免费无 PostgreSQL |
| GHCR 镜像仓库 | 免费，与 GitHub Actions 原生集成 |
| Sealos 部署 | 国内免费，支持 Docker 镜像 |
| Capacitor APK | 一套代码同时支持 Web + Android |
| JWT Query Param | window.open 下载文件无法携带 Header |
| 异步批改异常隔离 | 批改失败不影响已保存报告 |
