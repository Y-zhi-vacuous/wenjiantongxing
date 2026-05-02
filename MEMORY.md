# MEMORY.md — 文鉴同行 v1.0

AI 深圳中考作文批改平台。`https://wppyqjhwlqso.usw-1.sealos.app`

## 开发历程

设计→后端(8表/JWT/CRUD/OCR/GLM-4)→前端(15页/Apple UI)→部署(8轮调试/SSH)→AI优化

## AI 系统

### 评分: 两步法
1. 独立 API 判切题(temperature=0)
2. 注入判定结果评分
3. 后端 clamp 硬上限

### 能力: AI 驱动
综合所有历史报告 → GLM-4 生成评估+优先改进+五维措施
降级: 关键词匹配

### OCR: 容错链
glm-4.1v-thinking-flash(thinking:disabled) → 3重试 → glm-4v

## 评分维度 (45分)
立意10 | 内容15 | 语言10 | 结构5 | 文面5
离题≤10 | 偏题≤29

## 部署调试
标签大小写/GHCR权限/SQLite路径/bcrypt/Git push/Java版本/中文路径/event loop/thinking输出/限流/评分超限/离题高分/能力差 → 全部解决

## v2.0
PostgreSQL | AI写作辅导 | 教师仪表盘 | iOS | 推送
