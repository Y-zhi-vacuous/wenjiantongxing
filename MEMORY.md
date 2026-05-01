# MEMORY.md — 文鉴同行开发全纪录

## 项目概要

「文鉴同行」是一个 AI 驱动的深圳中考作文批改平台。从零到 v1.0 交付，完整经历需求设计 → 全栈开发 → 部署上线 → APK 构建。

**公网地址**: `https://wppyqjhwlqso.usw-1.sealos.app`

---

## 开发历程

### 阶段 1：需求澄清 (2026-04-30)
- 8 轮对话确定：深圳中考、Web+APK、学生+教师双角色
- 架构选型：FastAPI + React（对比 Jinja2 SSR、Vue SPA）
- 视觉打样：浏览器推送 Apple Native 风格线框图，用户确认

### 阶段 2：后端开发
- 8 张数据表，含 StudentAbility 能力画像
- JWT 双模式认证 (Header + Query Param)
- 作文 CRUD + 3 种上传方式（在线/文件/拍照）
- xlsx 批量导入导出学生
- 智谱 GLM-4 真实 AI 批改
- 学生能力分析：四维画像 + 分数趋势 + 优劣势 + 分维度改进计划

### 阶段 3：前端开发
- Apple Native UI：毛玻璃(backdrop-blur)、20px 大圆角、多层阴影
- 学生端 8 页 + 教师端 7 页
- 双击教师端学生卡片 → 详细能力画像
- 作文原文 + OCR 识别结果展示

### 阶段 4：部署 (最耗时)
- **8 轮调试**才成功：
  1. 镜像标签大写 → 硬编码全小写
  2. GHCR 默认私有 → 手动改 Public
  3. SQLite 连接失败 → 绝对路径 + mkdir
  4. bcrypt 版本不兼容 → 锁定 4.0.1
  5. Dockerfile 合并冲突 → 本地清理
  6. Git push 断断续续 → SSH Key 永久修复
  7. APK Java 版本 → 从 17 升级到 21
  8. APK 中文路径 → android.overridePathCheck

### 阶段 5：APK 构建
- Capacitor 8 + Java 21 + Android SDK 36
- 教师登录 → 自动进教师端，学生登录 → 自动进学生端
- API 指向公网服务器，无需配置

---

## 技术架构

```
浏览器 / Android APK
    │ HTTPS
    ▼
Sealos (免费 K8s)
    │
    ├── FastAPI (uvicorn, port 8080)
    │   ├── /api/* → REST API
    │   ├── /assets/* → 静态文件
    │   └── /* → index.html (SPA)
    │
    ├── SQLite (/app/data/essay_app.db)
    ├── 智谱 GLM-4 (批改)
    └── 智谱 GLM-4V (OCR)
```

## v1.0 现存问题

| # | 问题 | 影响 | 优先级 |
|---|------|------|--------|
| 1 | SQLite 数据不持久（容器重启丢失） | 高 | 🔴 |
| 2 | Sealos 免费休眠（15 分钟无访问停服） | 中 | 🟡 |
| 3 | 无 iOS 版本 | 中 | 🟡 |
| 4 | 批改无进度推送（需手动刷新） | 低 | 🟢 |
| 5 | 图片 OCR 偶尔慢（>15s） | 低 | 🟢 |
| 6 | APK 为 Debug 版（正式版需签名） | 低 | 🟢 |
| 7 | 无离线缓存 | 低 | 🟢 |

## v2.0 规划

### 核心功能
- **AI 写作辅导**：审题引导 → 构思支架 → 段落起草 → AI 实时反馈
- **教师教学仪表盘**：班级得分分布、进步曲线、薄弱点热力图
- **AI 出题 Agent**：按深圳中考趋势自动生成模拟题
- **批改报告 PDF 导出**：学生/教师可下载打印

### 基础设施
- **PostgreSQL 迁移**：替换 SQLite，解决数据持久化
- **UptimeRobot 防休眠**：免费监控，每 5 分钟 ping
- **iOS 支持**：Capacitor iOS 构建
- **Release APK 签名**：正式发布版本
- **文件存储**：对接 MinIO/S3 存储上传文件
- **CI 自动构建 APK**：GitHub Actions 自动出包

### 体验优化
- **推送通知**：批改完成后通知学生
- **离线模式**：PWA Service Worker 缓存
- **暗色模式**：深色主题支持

---

## 数据库表

| 表 | 用途 | 关键字段 |
|----|------|----------|
| users | 用户 (学生+教师) | role, real_name, teacher_cert |
| essay_topics | 作文题目 | word_requirement, time_minutes, extra_requirements |
| essays | 学生作文 | status(submitted/grading/graded), word_count |
| essay_reports | AI 批改报告 | total_score, paragraph_reviews(JSON), suggestions(JSON) |
| student_abilities | 能力画像 | content/language/structure/penmanship_ability |
| ai_configs | AI 配置 | provider, model_name, api_key_encrypted |
| classes / class_students | 班级管理 | teacher_id, student_id |

---

## 用户决策记录

- 部署平台偏好：免费、国内可访问 → Sealos
- AI 服务：智谱 API（默认），UI 可切换
- UI 风格：Apple Native（毛玻璃/大圆角/阴影）
- Git push：SSH 方式（国内网络稳定）
- 学生无需自己注册 → 教师统一创建
- 教师需实名注册（真名+学校+资格证号）
- 题目必须有写作要求（字数/时间/附加规则）
