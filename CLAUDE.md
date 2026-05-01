# CLAUDE.md — 文鉴同行

深圳中考 AI 作文批改平台。FastAPI + React + 智谱 GLM-4 + Sealos 部署。

## 常用命令

```bash
# 本地开发
cd backend && uvicorn app.main:app --reload --port 8000
cd backend && python -m app.seed                          # 初始化种子数据
cd frontend && npm install && npm run dev                  # 开发服务器 :5173 (Vite proxy /api → :8000)

# 构建
cd frontend && npm run build                              # Web 构建 → dist/
cd frontend && npx cap sync android                       # 同步到 Android
cd frontend/android && ./gradlew assembleDebug            # APK 构建 (需要 Java 21 + Android SDK 36)

# 部署 (全自动)
git push                                                  # SSH: git@github.com:Y-zhi-vacuous/wenjiantongxing.git
# → GitHub Actions 自动构建 Docker 镜像 → GHCR
# → Sealos Restart 拉取新镜像
```

## 技术栈

| 层 | 技术 | 路径 |
|----|------|------|
| 前端 | React 18 + TS + Vite + Tailwind | `frontend/src/` |
| 移动端 | Capacitor 8 Android | `frontend/android/` |
| 后端 | FastAPI + SQLAlchemy 2.0 | `backend/app/` |
| 数据库 | SQLite (dev/prod) / PostgreSQL | `backend/app/db.py` |
| AI 批改 | 智谱 GLM-4 | `backend/app/agents/grader.py` |
| 图片 OCR | 智谱 GLM-4V | `backend/app/services/parsing.py` |
| CI/CD | GitHub Actions → GHCR → Sealos | `.github/workflows/deploy.yml` |

## 项目结构

```
frontend/src/
├── pages/student/        # Dashboard / WriteEssay / EssayReport / History / Ability / Settings
├── pages/teacher/        # Dashboard / ClassList / ClassDetail / Topics / EssayView / StudentAbility
├── components/           # StudentNav / TeacherNav
├── api/client.ts         # Axios (baseURL from config.ts)
└── config.ts             # Web: /api  |  APK: https://wppyqjhwlqso.usw-1.sealos.app/api

backend/app/
├── models/   (8 models)  # User / Essay / EssayTopic / EssayReport / AIConfig / Class / ClassStudent / StudentAbility
├── api/      (7 routers) # auth / essays / topics / classes / ability / config / students
├── services/             # grading (AI批改编排) / parsing (OCR) / ability (画像更新)
├── agents/               # grader (GLM-4) / router
└── auth/                 # JWT (Header + Query Param 双模式)
```

## 关键决策

| 决策 | 理由 |
|------|------|
| GLM-4V 做 OCR | 免装 Tesseract，手写体识别更准，Docker 镜像更小 |
| SQLite 生产 | 零配置，Sealos 免费无 PostgreSQL |
| SSH Git push | 国内 GFW 阻断 HTTPS git，SSH 永久稳定 |
| bcrypt==4.0.1 | passlib 与新版 bcrypt 不兼容 |
| APK 构建需 Java 21 | AGP 8.13 + compileSdk 36 |
| android.overridePathCheck=true | 项目路径含中文 |
| JWT Query Param | window.open() 无法携带 Authorization header |

## 测试账号

| 角色 | 用户 | 密码 |
|------|------|------|
| 教师 | teacher1 | test123 |
| 学生 | student1 | test123 |

## 公网

- Web: `https://wppyqjhwlqso.usw-1.sealos.app`
- API: `https://wppyqjhwlqso.usw-1.sealos.app/api/health`
- GHCR: `ghcr.io/y-zhi-vacuous/wenjiantongxing:latest`
