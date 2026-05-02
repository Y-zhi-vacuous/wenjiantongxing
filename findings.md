# Findings

## v2.0 状态
- v2.0 架构重构完成
- 学生端: OCR 配置 + 作文提交 (不自动批改)
- 教师端: 评分配置 + 单篇/批量批改 + 能力刷新
- 公网: `https://wppyqjhwlqso.usw-1.sealos.app`

## 技术 v2.0
React 18 + TS + Vite + Tailwind + Capacitor 8 | FastAPI + SQLAlchemy + SQLite
评分: 统一 call_llm → 6 providers (Zhipu/OpenAI/DeepSeek/Claude/Ollama/vLLM)
OCR: glm-4.1v-thinking-flash(disabled) → glm-4v (学生 OCRConfig)

## v2.0 架构决策
| 决策 | 理由 |
|------|------|
| 评分迁移教师端 | 教师控制评分质量，可选付费API或本地部署 |
| 统一路由层 call_llm | 一种接口调用 6 个提供商 |
| 串行逐篇批改 | 避免并发 API 限流 |
| Prompt 独立模块 | 易于迭代优化 |
| 能力分析含教学建议 | 教师可直接获得可执行的教学方案 |

## 评分 (五维 45 分)
| 立意(10) | 内容(15) | 语言(10) | 结构(5) | 文面(5) |
切题硬限: 离题≤10 / 偏题≤29 | 字数: <100≤10 / 100-300≤29 / 300-500≤34

## v2.0 新特性
- 幂等数据迁移 (AIConfig → OCRConfig + GradingConfig)
- 切题检查 JSON 输出 (含 confidence + reasoning)
- 能力分析新增: teaching_recommendations + error_patterns

## OCR
thinking:disabled + 3次重试(4/8/12s) + glm-4v降级 + >500KB压缩 + 学生OCRConfig

## 部署调试
| 问题 | 解 |
|------|-----|
| 镜像标签大写 | 硬编码小写 |
| GHCR 401 | Public |
| SQLite连接 | 绝对路径+mkdir |
| bcrypt | 4.0.1 |
| Git push | SSH Key |
| OCR event loop | 异步 await |
| OCR 短输出 | thinking disabled |
| OCR 限流 | 重试+降级 |
| 评分超满分 | 后端 clamp |
| 离题高分 | topic_match 硬限 |
| 能力分析差 | AI报告驱动 |
| v2.0 配置分离 | OCRConfig + GradingConfig + migration |
