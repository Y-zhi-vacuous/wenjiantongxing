# 文鉴同行 v2.0

深圳中考 AI 作文批改。Web + Android APK。

🔗 `https://wppyqjhwlqso.usw-1.sealos.app`

## v2.0 架构

**学生端**: OCR 配置 → 提交作文 → 等待批改
**教师端**: 配置评分模型 → 单篇/批量批改 → 能力分析自动更新

## 评分 (两步法，五维 45 分)

独立切题检查 → 注入判定评分 → 后端硬限制
立意(10)+内容(15)+语言(10)+结构(5)+文面(5)=45
离题≤10 / 偏题≤29

## 多提供商（教师可配置）

云端: 智谱 GLM / OpenAI / DeepSeek / Claude
本地: Ollama / vLLM

## 能力分析 v2.0

教师触发 · AI 综合历史报告 · 教学建议(本周/2周/1月) · 共性错误识别

## 技术

React 18 + FastAPI + SQLite + 智谱 GLM-4 (评分) + GLM-4V (OCR)

## 测试

teacher1 / student1 (test123)
