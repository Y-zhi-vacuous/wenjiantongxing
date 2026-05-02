# Findings

## 状态
- v1.0 交付 | 公网: `https://wppyqjhwlqso.usw-1.sealos.app`
- Web + APK 双端运行

## 技术
React 18 + TS + Vite + Tailwind + Capacitor 8 | FastAPI + SQLAlchemy + SQLite
评分: GLM-4-Flash-250414 | OCR: glm-4.1v-thinking-flash(disabled) → glm-4v

## 评分 (五维 45 分)
| 立意(10) | 内容(15) | 语言(10) | 结构(5) | 文面(5) |
切题硬限: 离题≤10 / 偏题≤29 | 字数: <100≤10 / 100-300≤29 / 300-500≤34

## OCR
thinking:disabled + 3次重试(4/8/12s) + glm-4v降级 + >500KB压缩

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
