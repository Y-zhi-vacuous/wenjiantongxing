# 文鉴同行 — 系统设计文档

**日期**: 2026-04-30 | **更新**: 2026-05-01 | **状态**: 一期 MVP 交付 | **目标用户**: 深圳中考初中生

---

## 1. 项目目标

「文鉴同行」是一个 AI 驱动的 Web 应用，专为深圳中考学生设计。一期 MVP 提供 AI 自动批改 + 写作能力画像分析。二期将加入 AI 陪伴式写作辅导和教师教学仪表盘。

---

## 2. 需求决策汇总

| 维度 | 决策 |
|------|------|
| 目标用户 | 深圳中考初中生 |
| 平台 | Web 优先（桌面应用为降级方案） |
| 交互模式 | 作文批改（MVP）+ 写作辅导（二期） |
| AI 后端 | 混合方案：本地模型 + 云端 API，UI 可配置 |
| 用户角色 | 学生端 + 教师端，角色分离 |
| 题目来源 | 内置题库 + 教师自定义 |
| 提交方式 | 纯文本录入 + 文件上传 (doc/docx/pdf) |
| 技术栈 | FastAPI + React 前后端分离 |
| 前端风格 | Apple Native — 毛玻璃、大圆角、极简排版 |

---

## 3. 分期规划

### 一期 MVP：作文批改
- 教师实名注册 → 创建班级 → 创建/导入学生账号
- 学生登录 → 选题（查看写作要求）→ 提交作文（文本/文件/拍照）→ AI 批改 → 查看报告
- 能力画像自动更新（每次批改后）
- 学生修改密码
- xlsx 批量导入导出学生信息
- AI 配置面板

### 二期：写作辅导
- 审题引导 → 构思支架 → 段落起草 → 自评修改
- 教师教学仪表盘：班级得分分布、薄弱点分析、进步曲线
- AI 出题 Agent：智能生成模拟题

---

## 4. 系统架构

```
浏览器 (React SPA)
  ├── 学生端
  └── 教师端
       │ HTTPS / REST / WebSocket
       ▼
FastAPI 后端
  ├── 认证鉴权 (JWT)
  ├── 文件解析 (docx/pdf)
  ├── 题目库 & 班级管理
  └── 学习进度追踪
       │
       ▼
AI 智能体层
  ├── 批改 Agent — 评分 + 逐段点评 + 建议
  ├── 辅导 Agent（二期）— 审题→构思→起草→修改
  ├── 出题 Agent（二期）— 智能生成题目
  └── 模型路由器 — 本地/云端调度，UI 可配
       │
       ▼
PostgreSQL / Redis / MinIO(S3)
```

---

## 5. AI 智能体设计

### 5.1 Agent 矩阵

| Agent | 职责 | 时期 |
|-------|------|------|
| 批改 Agent | 分项评分 + 逐段精批 + 修改示例 + 总评 + 提升建议 | 一期 |
| 辅导 Agent | 审题引导 → 构思支架 → 段落起草 → 自评修改 | 二期 |
| 出题 Agent | 按深圳中考趋势生成模拟题，附审题提示 | 二期 |
| 模型路由器 | 统一模型调度，UI 可切换，云端不可用时降级本地 | 一期 |

### 5.2 批改工作流（6 步）

1. **文本预处理**：解析 docx/pdf → 纯文本 → 统计字数/段落数
2. **基础检测（本地模型）**：错别字、病句、标点错误（低延迟）
3. **内容分析（云端 API）**：审题准确度、立意深度、素材运用、结构逻辑
4. **分项评分（云端 API）**：内容 40% + 语言 30% + 结构 20% + 卷面 10%，对标深圳中考
5. **点评生成（云端 API）**：总评 + 逐段批注 + 改进建议 + 范文片段
6. **结果组装**：合并基础检测 + 云端分析 → 结构化批改报告

### 5.3 模型配置

用户可在 UI 设置面板配置：
- 本地模型选择（Ollama - Qwen2.5-7B / DeepSeek-R1-8B 等）
- 云端 API 选择（Claude / OpenAI / 通义千问 / DeepSeek API）
- API Key 填入
- 路由策略（智能路由 / 全走云端 / 全走本地）

---

## 6. 数据模型

### 核心表

**User** — id, username, password_hash, role(student/teacher), display_name, grade, school, created_at

**Class** — id, name, teacher_id(FK→User), created_at

**ClassStudent** — id, class_id(FK), student_id(FK→User), joined_at

**EssayTopic** — id, title, type(命题/半命题/材料/话题), genre(记叙文/议论文), difficulty, source(system/teacher), creator_id(FK), tips, created_at

**Essay** — id, student_id(FK), topic_id(FK), title, content, word_count, status(draft/submitted/graded), submitted_at, graded_at

**EssayReport** — id, essay_id(FK), total_score, score_content, score_language, score_structure, score_penmanship, basic_errors(JSON), paragraph_reviews(JSON), overall_comment, suggestions(JSON), model_used, processing_time_ms, created_at

**AIConfig** — id, user_id(FK), provider, model_name, api_key_encrypted, routing_strategy, is_active

---

## 7. REST API

| 模块 | 端点 |
|------|------|
| 认证 | POST /api/auth/register, POST /api/auth/login, GET /api/auth/me |
| 作文 | POST /api/essays/upload, GET /api/essays/{id}, GET /api/essays, GET /api/essays/{id}/report |
| AI 批改 | POST /api/essays/{id}/grade, GET /api/essays/{id}/grade-status, WS /ws/essays/{id}/grade |
| 题库 | GET /api/topics, POST /api/topics, GET /api/topics/{id} |
| 班级 | POST /api/classes, POST /api/classes/{id}/students, GET /api/classes/{id}/essays |
| AI 配置 | GET /api/config/ai, PUT /api/config/ai, POST /api/config/ai/test |

---

## 8. 前端设计

### 8.1 技术栈
- React 18 + TypeScript + Vite
- Tailwind CSS（backdrop-blur、自定义 Apple 色板）
- shadcn/ui（Radix 无样式组件基座）
- Framer Motion（页面过渡、微交互）
- Lucide Icons（线条风格图标）
- TipTap / Slate.js（富文本编辑器）
- Recharts / ECharts（教师仪表盘 二期）

### 8.2 设计语言 — Apple Native
- 毛玻璃导航（backdrop-filter: blur(20px)）
- 大圆角卡片（16-20px）
- 柔和多层阴影
- 大量留白、宽松行距
- 浅色模式底色 #F5F5F7，深色模式底色 #000
- 强调色：系统蓝 #007AFF
- 文字层级：#1D1D1F(主) / #6E6E73(辅) / #C7C7CC(禁用)

### 8.3 学生端页面
- /login — 登录（学生由教师创建账号后登录）
- /register — 教师实名注册
- /student/dashboard — 首页（统计卡片 + 能力快照 + 作文列表）
- /student/write — 选题（含写作要求展示）→ 录入/上传/拍照 → 提交
- /student/essay/:id — 批改报告（评分卡 + 基础检测 + 逐段点评 + 总评 + 建议）
- /student/history — 写作历史
- /student/ability — 能力画像（四维能力值 + 趋势 + 优劣势 + AI 改进计划）
- /student/settings — 修改密码 + AI 配置

### 8.4 教师端页面
- /teacher/dashboard — 教师工作台（统计 + 快捷入口 + 最近作文）
- /teacher/classes — 班级管理
- /teacher/classes/:id — 班级学生列表（能力查看 + 创建账号 + 模板/导入/导出）
- /teacher/topics — 题库管理（含写作要求字段）
- /teacher/essays/:id — 查看学生作文与批改报告
- /teacher/settings — 设置

### 8.5 批改报告页（核心页面结构）
- 总分大号居中 → 分项评分横排
- 基础检测卡片（错别字/病句/标点计数）
- 逐段点评（蓝色左边框标注，原文 → 点评）
- 总评段落
- 编号提升建议列表

---

## 9. 后端项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py             # 配置管理
│   ├── models/               # SQLAlchemy 模型
│   ├── schemas/              # Pydantic 请求/响应
│   ├── api/                  # 路由 handlers
│   ├── services/             # 业务逻辑
│   │   ├── grading.py        # 批改流程编排
│   │   └── parsing.py        # docx/pdf 解析
│   ├── agents/               # AI Agent 层
│   │   ├── router.py         # 模型路由器
│   │   ├── grader.py         # 批改 Agent
│   │   └── prompts/          # Prompt 模板
│   ├── auth/                 # JWT 认证
│   └── db.py                 # 数据库连接
└── requirements.txt

frontend/
├── src/
│   ├── pages/                # 页面组件
│   ├── components/           # 通用组件
│   ├── hooks/                # 自定义 hooks
│   ├── lib/                  # 工具函数
│   └── styles/               # Tailwind 配置
├── package.json
└── vite.config.ts
```
