# MEMORY.md — 文鉴同行 完整开发总结

## 项目概要

「文鉴同行」是一个 AI 驱动的深圳中考作文批改平台，支持 Web + Android APK。
公网：`https://wppyqjhwlqso.usw-1.sealos.app`
GitHub：`https://github.com/Y-zhi-vacuous/wenjiantongxing`

---

## 开发时间线

### 04-30：需求与设计
8 轮需求对话 → FastAPI+React 架构选型 → Apple Native 视觉打样确认

### 05-01：全栈开发
- **后端** 35 文件：8 数据表、JWT 双模式、3 种上传、GLM-4 批改+OCR、xlsx 导入导出
- **前端** 22 文件：Apple UI、学生 8 页+教师 7 页、轮询同步、原文展示
- **功能迭代**：深圳真题题库、更名文鉴同行、教师实名注册、学生账号管理、UI 美化

### 05-01 晚：部署
8 轮调试（标签大小写/GHCR权限/SQLite路径/bcrypt/Git push/Java版本/中文路径）→ SSH Key 永久修复 → Sealos 上线

### 05-01~02：AI 深度优化
- **OCR** 6 轮：event loop→thinking→模型名→图片压缩→限流重试+降级
- **评分** 5 轮：四维→六类文标准表→强制扣分→五维立意→两步法（独立切题检查+注入判定+后端硬限制）
- **能力** 2 轮：模板化→AI 综合历史报告生成个性化评估+优先改进+五维措施

---

## 技术架构

```
浏览器 / Android APK (Capacitor)
    │ HTTPS
    ▼
Sealos K8s (免费)
    ├── FastAPI :8080 (API + 静态文件 + SPA)
    ├── SQLite /app/data/
    ├── 评分: 两步法 (切题检查→评分→clamp)
    ├── OCR: 压缩→重试(3次)→降级(glm-4v)
    └── 能力: 历史报告→GLM-4综合分析
```

## AI 系统

### 评分（两步法）
1. 独立 API 判切题 (temperature=0, 专用Prompt)
2. 注入判定结果评分 (`【系统已判定：XXX】`)
3. 后端硬限制 (离题≤10/偏题≤29/各项不超满分)

### 五维评分 (45分)
| 立意 | 内容 | 语言 | 结构 | 文面 |
|------|------|------|------|------|
| 10 | 15 | 10 | 5 | 5 |

### OCR 容错链
glm-4.1v-thinking-flash(thinking:disabled) → 4/8/12s重试 → glm-4v降级

### 能力分析
历史报告 → GLM-4 生成：综合评估 + 优先改进 + 五维(assessment+action_items) + 趋势
降级：关键词匹配

## 15 个部署问题全部解决

| # | 问题 | 解决 |
|---|------|------|
| 1 | 镜像标签大写 | 硬编码小写 |
| 2 | GHCR 401 | Public |
| 3 | SQLite 连接 | 绝对路径+mkdir |
| 4 | bcrypt | 4.0.1 |
| 5 | Dockerfile 冲突 | 清理标记 |
| 6 | Git push | SSH Key |
| 7 | Java 版本 | Java 21 |
| 8 | 中文路径 | overridePathCheck |
| 9 | OCR event loop | await |
| 10 | OCR 18字 | thinking:disabled |
| 11 | OCR 模型名 | glm-4v |
| 12 | OCR 图片大 | PIL 压缩 |
| 13 | OCR 限流 | 重试+降级 |
| 14 | 评分超满分 | clamp |
| 15 | 离题高分 | 两步法 |

## 统计
~30 commits / ~8500 行 / 后端35文件 / 前端22文件 / 文档8文件
