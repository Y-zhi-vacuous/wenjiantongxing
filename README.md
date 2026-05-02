# 文鉴同行 v2.1

深圳中考 AI 作文批改。Web + Android APK。

🔗 `https://wppyqjhwlqso.usw-1.sealos.app`

## v2.1 评分（深圳市官方标准，四维 45 分）

内容(15, 含立意) + 语言(15) + 结构(10) + 文面(5) = 45
偏题: 内容≤6 总分≤25 / 离题: 内容≤3 总分≤10

## v2.0 架构

**学生端**: OCR 配置 → 提交 → 等待
**教师端**: 评分+能力配置 → 单篇/批量批改 → 能力自动更新

## 多提供商（教师可配）
云端: 智谱/OpenAI/DeepSeek/Claude · 本地: Ollama/vLLM

## 技术
React 18 + FastAPI + SQLite + 智谱 GLM-4

## 测试
teacher1 / student1 (test123)
