# CLAUDE.md — 文鉴同行 v2.1

深圳中考 AI 作文批改平台。FastAPI + React + 智谱 GLM-4 + Sealos。

## v2.1 评分标准

按照深圳市中考官方标准：**四维 15+15+10+5=45 分**

| 内容 (含立意) | 语言 | 结构 | 文面 |
|-------------|------|------|------|
| 15 | 15 | 10 | 5 |

- 切题检查判断「核心思想方向」是否契合题目（非描写篇幅占比）
- 偏题：内容≤6，总分≤25 / 离题：内容≤3，总分≤10

## v2.0 架构

- **学生端**：OCR 配置，提交作文后不触发批改
- **教师端**：评分+能力配置，支持 6 提供商（付费API 或本地部署），独立配置
- **教师触发批改**：单篇/一键全部（串行逐篇），批改后自动更新能力模型

## 常用命令

```bash
cd backend && uvicorn app.main:app --reload --port 8000
cd backend && python -m app.seed
cd frontend && npm run dev                # :5173
git push    # SSH: git@github.com:Y-zhi-vacuous/wenjiantongxing.git
```

## 技术栈

React 18 + TS + Vite + Tailwind + Capacitor 8 | FastAPI + SQLAlchemy + SQLite
评分: GLM-4-Flash-250414 (两步法) | OCR: glm-4.1v-thinking-flash→glm-4v
LLM 路由: 统一 call_llm 支持 Zhipu/OpenAI/DeepSeek/Claude/Ollama/vLLM

## 项目结构

```
frontend/src/pages/{student,teacher}/
backend/app/{models,api,services,agents,auth,migrations}/
backend/app/agents/prompts/             # Prompt 独立模块
```

## AI 评分系统（两步法）

1. **切题检查**（独立 API, temperature=0）→ 判断核心思想方向 → 切题/偏题/离题
2. **评分**（注入判定结果，temperature=0.7）→ 四维评分
3. **后端硬限**: 离题 内容≤3 总分≤10 / 偏题 内容≤6 总分≤25
4. 使用教师 GradingConfig 配置的提供商和模型

## 能力分析

教师触发，AI 综合历史报告: 综合评估 + 优先改进 + 四维分析 + 教学建议 + 错误模式

## 关键决策

官方四维评分标准 | 两步法审题优先 | 教师驱动评分+多提供商路由 | 默认模型勾选框 | 切题判定展示

## 公网

`https://wppyqjhwlqso.usw-1.sealos.app` | teacher1/student1 (test123)
