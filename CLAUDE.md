# CLAUDE.md — 文鉴同行

深圳中考 AI 作文批改平台。FastAPI + React + 智谱 GLM-4 + Sealos 部署。

## 常用命令

```bash
# 本地开发
cd backend && uvicorn app.main:app --reload --port 8000
cd backend && python -m app.seed
cd frontend && npm run dev

# 构建
cd frontend && npm run build && npx cap sync android
cd frontend/android && ./gradlew assembleDebug          # APK (Java 21 + SDK 36)

# 部署
git push    # SSH: git@github.com:Y-zhi-vacuous/wenjiantongxing.git
# → Actions → GHCR → Sealos Restart
```

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 18 + TS + Vite + Tailwind + Capacitor 8 |
| 后端 | FastAPI + SQLAlchemy 2.0 + SQLite |
| 评分 AI | 智谱 GLM-4-Flash-250414 |
| OCR AI | glm-4.1v-thinking-flash (thinking disabled, 3重试 → glm-4v降级) |
| 部署 | GitHub Actions → GHCR → Sealos |

## 项目结构

```
frontend/src/
├── pages/student/   # Dashboard / WriteEssay / EssayReport / History / Ability / Settings
├── pages/teacher/   # Dashboard / ClassList / ClassDetail / Topics / EssayView / StudentAbility
└── config.ts        # Web /api  |  APK Sealos URL

backend/app/
├── models/   (8)    # User / Essay / EssayTopic / EssayReport / AIConfig / Class / ClassStudent / StudentAbility
├── api/      (7)    # auth / essays / topics / classes / ability / config / students
├── services/        # grading(clamp + topic_match) / parsing(OCR retry) / ability(AI-driven)
├── agents/          # grader(GLM-4) / router
└── auth/            # JWT (Header + Query Param)
```

## AI 评分系统

### 五项维度 (满分 45)
| 维度 | 满分 |
|------|------|
| 立意 | 10 |
| 内容 | 15 |
| 语言 | 10 |
| 结构 | 5 |
| 文面 | 5 |

### 切题硬限制 (后端强制)
| topic_match | 立意≤ | 总分≤ |
|-------------|-------|-------|
| 切题/基本切题 | 10 | 45 |
| 部分偏题 | 5 | 29 |
| 完全离题 | 2 | 10 |

### 字数限制
<100字≤10 / 100-300≤29 / 300-500≤34

### 能力分析
- 五维度画像，百分制
- 改进建议从 AI 批改历史中按维度关键词提取，非模板

### 模型可配置
- 评分: `AI_GRADING_MODEL` 环境变量或设置页
- OCR: `AI_OCR_MODEL` 环境变量或设置页

## 关键决策

| 决策 | 理由 |
|------|------|
| Prompt 审题第一步 | 防止 AI 对离题作文打高分 |
| 后端 clamp + topic_match 硬限制 | AI 有时不遵守自身上限 |
| glm-4.1v-thinking-flash thinking:disabled | OCR 准确但需关思考模式 |
| 能力分析从报告提取建议 | 废弃模板化文案 |
| bcrypt==4.0.1 | passlib 兼容 |
| SSH Git | 国内永久稳定 |
| android.overridePathCheck | 中文路径 |

## 公网 & 测试

- Web: `https://wppyqjhwlqso.usw-1.sealos.app`
- test: teacher1 / student1 (test123)
