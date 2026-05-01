# 文鉴同行 — 开发总结

## 项目概述

「文鉴同行」是一个 AI 驱动的深圳中考作文批改平台。从零开始，经历需求澄清 → 架构设计 → 全栈开发 → 部署上线的完整流程。

## 开发时间线

### 阶段 1：需求澄清与架构设计 (2026-04-30)
- 8 轮对话确定：深圳中考、Web 优先、双角色（学生+教师）、AI 批改+辅导
- 3 种架构对比后选择 FastAPI + React 前后端分离
- 可视化设计稿（Apple Native 风格）推送浏览器确认

### 阶段 2：后端开发
- 8 张数据表：User / Essay / EssayTopic / EssayReport / AIConfig / Class / ClassStudent / StudentAbility
- JWT 认证 + Query Param 双模式（解决文件下载认证）
- 作文 CRUD + 文件解析（docx/pdf/image）
- xlsx 批量导入导出学生账号
- 学生能力分析：每次批改后自动更新四维画像 + 趋势 + 改- 进计划

### 阶段 3：前端开发
- Apple Native 风格：毛玻璃（backdrop-blur）、大圆角（20px）、多层阴影、渐变背景
- 学生端 8 页：登录/注册/首页/写作/批改报告/历史/能力/设置
- 教师端 7 页：工作台/班级管理/学生能力详情/题库/作文查看/设置
- GLM-4V 视觉模型替代本地 OCR

### 阶段 4：部署
- GitHub Actions 自动构建 Docker 镜像 → GHCR
- Sealos 免费托管（国内访问快）
- **部署调试了 8 轮**：镜像标签大小写 / 包权限 / SQLite 路径 / bcrypt 兼容 / Dockerfile 合并冲突 / Git push 不稳定
- 最终方案：SSH Key 永久解决 Git 连接问题

## 关键技术决策

| 决策 | 理由 |
|------|------|
| 智谱 GLM-4 批改 | 中文理解好，价格低，国内访问快 |
| GLM-4V 图片 OCR | 免安装 Tesseract，手写体识别更准 |
| SQLite 生产环境 | 零配置，Sealos 免费无 PostgreSQL |
| SSH Git push | 国内网络稳定，不受 GFW 干扰 |
| Apple Native UI | 毛玻璃/大圆角/阴影，视觉品质高 |
| 异步批改+异常隔离 | AI API 可能超时，不影响已保存数据 |

## 部署流水线

```
本地开发 → git push (SSH) → GitHub Actions → Docker 镜像 → GHCR → Sealos Restart → 公网
```

## 已知问题 & 后续计划

- [ ] Android APK 构建（Capacitor 项目已初始化，待 Android Studio 构建）
- [ ] 二期：写作辅导（审题→构思→起草→修改）
- [ ] 二期：教师教学仪表盘
- [ ] 部署监控（UptimeRobot 防休眠）

## 用户偏好

- 不需要部署服务器，代码推 GitHub 后自动构建
- AI 默认使用智谱 API，UI 可切换
- 界面偏好 Apple 原生风格
- 文档与代码同步更新
