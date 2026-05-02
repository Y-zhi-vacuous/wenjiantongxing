# CLAUDE.md — 文鉴同行 v2.0

深圳中考 AI 作文批改平台。FastAPI + React + 智谱 GLM-4 + Sealos。

## v2.0 架构变化

- **学生端**：仅 OCR 配置，提交作文后不自动触发批改
- **教师端**：评分 + 能力分析配置，支持付费 API（Zhipu/OpenAI/DeepSeek/Claude）和本地部署（Ollama/vLLM）
- **教师触发批改**：单篇批改或一键全部批改（串行逐篇），批改后自动更新学生能力模型

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
LLM 路由: 统一 call_llm 支持 6 提供商

## 项目结构

```
frontend/src/pages/{student,teacher}/   # 学生8页 + 教师8页 (v2.0新增 GradingQueue)
backend/app/{models,api,services,agents,auth,migrations}/
backend/app/agents/prompts/             # v2.0: Prompt 独立模块
```

## AI 评分系统（两步法）

1. **切题检查**（独立 API，temperature=0，JSON 输出含 confidence）→ 输出: 切题/部分偏题/完全离题
2. **评分**（注入判定结果 `【系统已判定：部分偏题...】`）→ 五维评分
3. **后端硬限制**: 离题≤10 / 偏题≤29
4. **v2.0**: 使用教师 GradingConfig 配置的提供商和模型

### 五维 (满分45)
| 立意 | 内容 | 语言 | 结构 | 文面 |
|------|------|------|------|------|
| 10 | 15 | 10 | 5 | 5 |

## 能力分析 v2.0

教师触发，使用教师配置的模型。AI 综合所有历史报告生成:
- 综合评估 + 优先改进 + 五维分析(action_items) + 趋势
- v2.0 新增: 教学建议(本周/2周/1月) + 共性错误模式识别
- 降级: 关键词匹配

## 多提供商支持

统一路由层 `call_llm()` 支持:
- 云端: Zhipu, OpenAI, DeepSeek, Claude
- 本地: Ollama, vLLM

## 关键决策

两步法评分 | AI驱动能力分析 | thinking:disabled OCR | bcrypt==4.0.1 | SSH Git | v2.0: 教师驱动评分+多提供商路由

## 公网

`https://wppyqjhwlqso.usw-1.sealos.app` | teacher1/student1 (test123)
