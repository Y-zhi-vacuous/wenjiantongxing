# CLAUDE.md — 文鉴同行

深圳中考 AI 作文批改平台。FastAPI + React + 智谱 GLM-4 + Sealos。

## 常用命令

```bash
cd backend && uvicorn app.main:app --reload --port 8000   # 后端
cd backend && python -m app.seed                          # 种子数据
cd frontend && npm run dev                                # 前端 :5173
cd frontend && npm run build && npx cap sync android     # Web构建+APK同步
cd frontend/android && ./gradlew assembleDebug            # APK (Java21+SDK36)
git push    # SSH: git@github.com:Y-zhi-vacuous/wenjiantongxing.git
```

## 技术栈

React 18 + TS + Vite + Tailwind + Capacitor 8 | FastAPI + SQLAlchemy + SQLite
评分: GLM-4-Flash-250414 (两步法) | OCR: glm-4.1v-thinking-flash→glm-4v

## 项目结构

```
frontend/src/pages/{student,teacher}/   # 15页面
backend/app/{models,api,services,agents,auth}/
```

## AI 评分系统（两步法）

1. **切题检查**（独立 API，temperature=0，专用 Prompt）→ 输出: 切题/部分偏题/完全离题
2. **评分**（注入判定结果 `【系统已判定：部分偏题...】`）→ 五维评分
3. **后端硬限制**: 离题≤10 / 偏题≤29

### 五维 (满分45)
| 立意 | 内容 | 语言 | 结构 | 文面 |
|------|------|------|------|------|
| 10 | 15 | 10 | 5 | 5 |

## 能力分析

AI 综合所有历史报告生成: 综合评估 + 优先改进 + 五维分析(action_items) + 趋势
降级: 关键词匹配

## 关键决策

两步法评分 | AI驱动能力分析 | thinking:disabled OCR | bcrypt==4.0.1 | SSH Git

## 公网

`https://wppyqjhwlqso.usw-1.sealos.app` | teacher1/student1 (test123)
