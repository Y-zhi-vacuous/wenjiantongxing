# CLAUDE.md

## 项目：文鉴同行

深圳中考 AI 作文批改平台。FastAPI + React + 智谱 GLM-4 驱动。

## 常用命令

```bash
# 本地开发
cd backend && uvicorn app.main:app --reload --port 8000  # 后端
cd backend && python -m app.seed                          # 初始化数据
cd frontend && npm run dev                                # 前端 (端口 5173，Vite 代理 /api → :8000)

# 构建 & 部署
cd frontend && npm run build                              # 前端构建到 dist/
git push                                                  # 推送（已配置 SSH）
# GitHub Actions 自动构建 Docker → GHCR → Sealos 手动 Restart
```

## 技术栈

| 层 | 技术 | 路径 |
|----|------|------|
| 前端 | React 18 + TS + Vite + Tailwind | `frontend/src/` |
| 后端 | FastAPI + SQLAlchemy + SQLite | `backend/app/` |
| AI | 智谱 GLM-4 + GLM-4V | `backend/app/agents/grader.py` |
| OCR | GLM-4V 视觉模型 | `backend/app/services/parsing.py` |
| 部署 | GitHub Actions → GHCR → Sealos | `Dockerfile`, `.github/workflows/deploy.yml` |

## 项目架构

```
frontend/src/
├── pages/student/     # 登录/Dashboard/写作/报告/历史/能力/设置
├── pages/teacher/     # 工作台/班级管理/题库/作文查看/学生能力
├── components/        # 导航栏
├── api/client.ts      # Axios，baseURL 来自 src/config.ts
└── config.ts          # API_BASE_URL 切换（Web/APK）

backend/app/
├── models/            # 8 张表
├── api/               # REST 路由 (auth/essays/topics/classes/ability/config/students)
├── services/          # grading / parsing (OCR) / ability
├── agents/            # grader (GLM-4) / router
└── auth/              # JWT
```

## 关键注意

- **Git push 必须用 SSH**：`git@github.com:Y-zhi-vacuous/wenjiantongxing.git`，HTTPS 在国内不稳定
- **数据库路径**：生产用绝对路径 `sqlite+aiosqlite:////app/data/essay_app.db`，本地用相对路径
- **bcrypt 版本**：锁定 `bcrypt==4.0.1`，新版与 passlib 不兼容
- **前端 API**：Web 模式用相对 `/api`，APK 模式用绝对 URL（`src/config.ts`）
- **AI Key**：`.env` 中配置，不在代码中硬编码
- **CORS**：生产设 `*`，本地 `localhost:5173`

## 公网地址

- Web: `https://wppyqjhwlqso.usw-1.sealos.app`
- API: `https://wppyqjhwlqso.usw-1.sealos.app/api/health`
- GHCR: `ghcr.io/y-zhi-vacuous/wenjiantongxing:latest`

## 测试账号

| 角色 | 用户 | 密码 |
|------|------|------|
| 教师 | teacher1 | test123 |
| 学生 | student1 | test123 |
