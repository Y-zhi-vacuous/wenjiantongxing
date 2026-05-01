# Task Plan: 文鉴同行 — 实施总览

## Goal
构建 AI 作文批改系统「文鉴同行」：学生提交作文 → AI 批改 → 结构化报告 + 写作能力画像分析。

## Current Phase
交付完成

## Phases

### Phase 1: 项目脚手架搭建 ✅
- [x] 初始化后端项目 (FastAPI + SQLAlchemy + SQLite)
- [x] 初始化前端项目 (React + Vite + TypeScript + Tailwind)
- [x] Docker Compose 编排 PostgreSQL / Redis / MinIO
- [x] 配置 CORS、环境变量、.gitignore

### Phase 2: 后端核心 API ✅
- [x] SQLAlchemy 数据模型 (7 张表 + StudentAbility + 写作要求字段)
- [x] JWT 认证 (支持 Header + Query Param token)
- [x] 作文 CRUD API (创建/文本上传/文件上传/图片上传/查看/列表)
- [x] 文件解析服务 (docx / pdf / image → 纯文本)
- [x] 题目库 API (深圳中考真题 + 教师自定义，含写作要求)
- [x] 班级管理 API (创建/查看/添加学生/批量导入/导出)
- [x] AI 配置 API (读/写/测试连接)
- [x] 学生密码修改 API

### Phase 3: AI 智能体层 ✅
- [x] 模型路由器架构 (Ollama / 云端 API 接口预留)
- [x] 批改 Agent (Prompt 模板 + Mock 模式)
- [x] 批改流程编排 (异步任务 + 异常隔离)
- [x] 学生能力分析服务 (每次批改后更新四维能力画像)

### Phase 4: 前端学生端 ✅
- [x] 登录页 (Apple 风格，毛玻璃卡片)
- [x] 注册页 (教师实名注册)
- [x] 学生首页 Dashboard (统计卡片 + 能力快照 + 作文列表)
- [x] 作文提交页 (在线写作/文件上传/手写拍照 三模式)
- [x] 批改报告页 (评分卡 + 基础检测 + 逐段点评 + 总评 + 建议)
- [x] 写作历史页
- [x] 能力画像页 (四维雷达 + 分数趋势 + 优劣势 + AI 改进计划)
- [x] 设置页 (密码修改 + AI 配置)

### Phase 5: 前端教师端 ✅
- [x] 教师工作台 Dashboard
- [x] 班级管理 (创建/列表/学生能力查看)
- [x] 题库管理 (添加题目含写作要求)
- [x] 学生账号管理 (单个创建 + xlsx 批量导入/导出模板)
- [x] 查看学生作文 & 批改报告

### Phase 6: 增强功能 ✅
- [x] 深圳中考 8 道真题 (2017-2024) + 2 道模拟题
- [x] 真实写作要求 (600-900字、诗歌除外、匿名规则、诚信要求)
- [x] Apple Native UI (毛玻璃、半透明、多层阴影、微动效)
- [x] 应用更名为「文鉴同行」
- [x] 教师实名注册 (真实姓名+学校+教师资格证号)
- [x] 学生账号由教师统一创建管理

## Key Decisions
| Decision | Rationale |
|----------|-----------|
| SQLite 开发模式 | 无水 Docker 环境，aiosqlite 零配置 |
| Mock Agent 模式 | 开发阶段不依赖真实 API |
| JWT Header + Query Param | 支持文件下载 (window.open 无法携带 header) |
| openpyxl | 轻量 xlsx 操作，无需 Excel 安装 |
| 异步批改 + 异常隔离 | 批改失败不影响已保存的报告 |
| Apple 设计语言 | backdrop-blur + 大圆角 + 柔和阴影 |

## Architecture
```
React SPA (学生端 + 教师端)
    │ HTTPS / REST
    ▼
FastAPI 后端
    ├── Auth (JWT)
    ├── Essays (CRUD + upload)
    ├── AI Agents (批改 + 能力分析)
    ├── Topics (题库 + 写作要求)
    ├── Classes (班级 + 学生管理)
    └── Config (AI 配置)
    │
    ▼
SQLite (dev) / PostgreSQL (prod)
```
