# CLAUDE.md — 文鉴同行

深圳中考 AI 作文批改平台。FastAPI + React + 智谱 GLM-4 + Sealos 部署。

## 常用命令

```bash
# 本地开发
cd backend && uvicorn app.main:app --reload --port 8000
cd backend && python -m app.seed                          # 初始化种子数据
cd frontend && npm install && npm run dev                  # 开发服务器 :5173

# 构建
cd frontend && npm run build                              # Web 构建 → dist/
cd frontend && npx cap sync android                       # 同步到 Android
cd frontend/android && ./gradlew assembleDebug            # APK 构建 (Java 21 + SDK 36)

# 部署
git push                                                  # SSH: git@github.com:Y-zhi-vacuous/wenjiantongxing.git
# → Actions Docker → GHCR → Sealos Restart
```

## 技术栈

| 层 | 技术 | 路径 |
|----|------|------|
| 前端 | React 18 + TS + Vite + Tailwind | `frontend/src/` |
| 移动端 | Capacitor 8 Android | `frontend/android/` |
| 后端 | FastAPI + SQLAlchemy 2.0 | `backend/app/` |
| 数据库 | SQLite (dev/prod) | `backend/app/db.py` |
| AI 批改 | 智谱 GLM-4-Flash-250414 | `backend/app/agents/grader.py` |
| 图片 OCR | 智谱 glm-4.1v-thinking-flash (thinking disabled) + glm-4v 降级 | `backend/app/services/parsing.py` |
| CI/CD | GitHub Actions → GHCR → Sealos | `.github/workflows/deploy.yml` |

## 项目结构

```
frontend/src/
├── pages/student/        # Dashboard / WriteEssay / EssayReport / History / Ability / Settings
├── pages/teacher/        # Dashboard / ClassList / ClassDetail / Topics / EssayView / StudentAbility
├── components/           # StudentNav / TeacherNav
├── api/client.ts         # Axios (baseURL from config.ts)
└── config.ts             # Web: /api  |  APK: Sealos URL

backend/app/
├── models/   (8 models)  # User / Essay / EssayTopic / EssayReport / AIConfig / Class / ClassStudent / StudentAbility
├── api/      (7 routers) # auth / essays / topics / classes / ability / config / students
├── services/             # grading / parsing(OCR) / ability
├── agents/               # grader(GLM-4) / router
└── auth/                 # JWT (Header + Query Param)
```

## AI 评分系统

### 五项维度 (满分 45)
| 维度 | 满分 | 说明 |
|------|------|------|
| 立意 | 10 | 审题准确度、主题深度、角度新颖 |
| 内容 | 15 | 选材、详略、真情实感、细节描写 |
| 语言 | 10 | 表达流畅度、修辞、文采 |
| 结构 | 5 | 段落、过渡、首尾呼应 |
| 文面 | 5 | 卷面整洁、标点规范、错别字 |

### 切题硬限制
| 判定 | 立意上限 | 总分上限 |
|------|---------|---------|
| 切题/基本切题 | 10 | 45 |
| 部分偏题 | 5 | 29 |
| 完全离题 | 2 | 10 |

### OCR 模型
- 默认: `glm-4.1v-thinking-flash` (thinking disabled, 3次重试)
- 降级: `glm-4v` (限流时自动切换)
- 图片 >500KB 自动压缩

### 模型可配置
- 评分模型: 环境变量 `AI_GRADING_MODEL` 或设置页
- OCR 模型: 环境变量 `AI_OCR_MODEL` 或设置页

## 关键决策

| 决策 | 理由 |
|------|------|
| glm-4.1v-thinking-flash + thinking:disabled | OCR 准确但需关思考模式 |
| 五项评分 + 后端硬限制 | AI 不能越界打分 |
| bcrypt==4.0.1 | passlib 兼容性 |
| SSH Git push | 国内网络永久稳定 |
| android.overridePathCheck | 中文路径兼容 |

## 公网

- Web: `https://wppyqjhwlqso.usw-1.sealos.app`
- GHCR: `ghcr.io/y-zhi-vacuous/wenjiantongxing:latest`
- 测试: teacher1 / student1 (密码 test123)
