# 文鉴同行

深圳中考 AI 作文智能批改平台。学生提交作文 → AI 批改 → 结构化报告 + 写作能力画像分析。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 18 + TypeScript + Vite + Tailwind CSS |
| 后端 | FastAPI + SQLAlchemy (SQLite/PostgreSQL) |
| AI | Mock Agent (开发) / Claude API / OpenAI / DeepSeek / Ollama |
| 文件处理 | python-docx + pdfplumber + openpyxl |

## 快速启动

### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

首次启动自动创建数据库表。访问 http://localhost:8000/docs 查看 API。

### 2. 初始化数据

```bash
cd backend
python -m app.seed
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 测试账号

| 角色 | 用户名 | 密码 | 备注 |
|------|--------|------|------|
| 教师 | teacher1 | test123 | 实名: 李明远 |
| 学生 | student1 | test123 | 九(3)班 |

## 功能概览

### 学生端
- 选题写作（在线/文件上传/拍照上传）
- AI 批改报告（评分 + 逐段点评 + 总评 + 提升建议）
- 写作能力画像（四维能力值 + 历史趋势 + 优劣势 + 改进计划）
- 设置（修改密码 + AI 配置）

### 教师端
- 班级管理（创建班级 + 学生能力查看）
- 学生账号管理（单个创建 + xlsx 批量导入/导出）
- 题库管理（8道深圳中考真题 + 自定义题目 + 写作要求）
- 查看学生作文与批改报告
- 实名注册

## 项目结构

```
├── backend/app/
│   ├── models/       # 数据模型 (8 models)
│   ├── schemas/      # Pydantic 验证
│   ├── api/          # REST 路由 (7 modules)
│   ├── services/     # 业务逻辑 (grading, parsing, ability)
│   ├── agents/       # AI 智能体 (grader, router)
│   └── auth/         # JWT 认证
├── frontend/src/
│   ├── pages/student/ # 学生端 (8 pages)
│   ├── pages/teacher/ # 教师端 (6 pages)
│   ├── components/    # 通用组件
│   └── api/           # Axios 客户端
└── docs/superpowers/specs/  # 设计文档
```

## API 概览

| 模块 | 端点 |
|------|------|
| 认证 | POST /auth/register/teacher, POST /auth/login, PUT /auth/password |
| 学生管理 | POST /auth/register/student, GET /classes/{id}/students/template, POST /classes/{id}/students/import, GET /classes/{id}/students/export |
| 作文 | POST /essays, POST /essays/upload, POST /essays/upload-image, POST /essays/{id}/grade, GET /essays/{id}/report |
| 题库 | GET /topics, POST /topics |
| 能力分析 | GET /ability/me, GET /ability/student/{id} |
| AI 配置 | GET /config/ai, PUT /config/ai |
