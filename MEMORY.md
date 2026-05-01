# MEMORY.md — 文鉴同行 v1.0 开发全纪录

## 项目概要

「文鉴同行」—— AI 驱动的深圳中考作文批改平台。
公网: `https://wppyqjhwlqso.usw-1.sealos.app`

---

## 开发历程

### 阶段 1：需求设计 (2026-04-30)
- 8 轮对话确定：深圳中考、Web+APK、师生双角色
- FastAPI + React 架构选型、Apple Native 视觉打样

### 阶段 2：后端
- 8 张表、JWT 双模式认证、3 种上传方式
- 智谱 GLM-4 批改 + GLM-4V OCR
- 学生能力画像（四维 → 五维）
- xlsx 批量导入导出

### 阶段 3：前端
- Apple Native UI（毛玻璃/大圆角/阴影）
- 15 个页面、教师端学生能力详情
- 作文原文 + OCR 结果展示

### 阶段 4：部署
- 8 轮调试：标签大小写/GHCR权限/SQLite路径/bcrypt/合并冲突/Git push/Java版本/中文路径
- SSH Key 永久解决 Git 推送

### 阶段 5：AI 优化
- **评分系统重构**：五维度（立意10+内容15+语言10+结构5+文面5）
- **切题硬限制**：离题≤10分、偏题≤29分
- **OCR 容错**：3次重试 + glm-4v 降级
- **模型可配置**：OCR/评分模型独立设置

---

## 技术架构

```
浏览器 / Android APK
    │ HTTPS
    ▼
Sealos (免费 K8s)
    ├── FastAPI :8080 (API + 静态文件)
    ├── SQLite /app/data/
    ├── GLM-4-Flash-250414 (批改)
    └── glm-4.1v-thinking-flash → glm-4v (OCR)
```

## 评分系统

| 判定 | 立意 | 总分 |
|------|------|------|
| 切题 | ≤10 | ≤45 |
| 部分偏题 | ≤5 | ≤29 |
| 完全离题 | ≤2 | ≤10 |

## v1.0 问题 & v2.0 规划

| 优先级 | 问题 | 计划 |
|--------|------|------|
| 🔴 | 数据不持久 | PostgreSQL 迁移 |
| 🟡 | 免费休眠 | UptimeRobot |
| 🟡 | 无 iOS | Capacitor iOS |
| 🟢 | 无推送/离线 | PWA Service Worker |

v2.0: AI写作辅导、教师仪表盘、AI出题、PDF导出

## 用户决策

- Sealos (免费/国内快) | 智谱 API (默认) | Apple UI
- 教师创建学生账号 | 教师实名注册
- SSH Git push | 题目必有写作要求
