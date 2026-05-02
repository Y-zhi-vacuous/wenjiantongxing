# MEMORY.md — 文鉴同行 v1.0

## 项目概要

AI 驱动的深圳中考作文批改平台。公网: `https://wppyqjhwlqso.usw-1.sealos.app`

---

## 开发历程

### 设计 (04-30)
8 轮需求 → FastAPI+React 架构 → Apple Native 视觉打样

### 后端
8 张表、JWT 双模式、3 种上传、GLM-4 批改+GLM-4V OCR、xlsx 导入导出

### 前端
15 页面、Apple 风格 UI、教师端学生能力详情

### 部署
8 轮调试: 标签大小写/GHCR权限/SQLite路径/bcrypt/Git push/Java版本/中文路径 → SSH 永久修复

### AI 优化
- **评分**: 五维度+切题硬限制+Prompt审题第一步+后端clamp
- **OCR**: thinking disabled+3重试+glm-4v降级+图片压缩
- **能力**: 五项画像+AI报告驱动个性化建议

---

## 评分系统

| 维度 | 立意 | 内容 | 语言 | 结构 | 文面 | 总分 |
|------|------|------|------|------|------|------|
| 满分 | 10 | 15 | 10 | 5 | 5 | 45 |

切题硬限制: 离题≤10 / 偏题≤29

## OCR 容错链

glm-4.1v-thinking-flash → 限流? 等4/8/12s → 仍失败? → glm-4v → 仍失败? 报错

## v2.0 规划

- PostgreSQL 数据持久化
- AI 写作辅导 + 教师仪表盘 + AI 出题 + PDF 导出
- iOS + 推送通知 + 暗色模式

## 用户决策

Sealos(免费国内) / 智谱API / Apple UI / 教师管学生 / SSH Git / 题目必有写作要求
