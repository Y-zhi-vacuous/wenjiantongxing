# Findings

## 当前状态
- 应用名: 文鉴同行
- 公网地址: `https://wppyqjhwlqso.usw-1.sealos.app`
- GitHub: `https://github.com/Y-zhi-vacuous/wenjiantongxing`
- SSH Push: ✅ 永久修复

## 技术栈
- 前端: React 18 + TypeScript + Vite + Tailwind CSS + Capacitor
- 后端: FastAPI + SQLAlchemy + SQLite
- AI: 智谱 GLM-4 (批改) + GLM-4V (OCR 识别)
- 部署: GitHub Actions → GHCR → Sealos
- 移动端: Capacitor Android (待构建)

## 深圳中考标准
- 满分 45 分 (含书写 3 分)
- 字数 600-900，除诗歌外不限
- 匿名规则 (XXX 代替)、不得抄袭套作
- 8 道真题 (2017-2024) + 2 道模拟题

## API 概览
| Module | Endpoints |
|--------|------|
| Auth | POST /register/teacher, POST /register/student, POST /login, PUT /password |
| Essays | POST /, POST /upload, POST /upload-image, POST /{id}/grade, GET /{id}/report |
| Topics | GET /, POST / |
| Classes | GET /, POST /, GET /{id}/students/template, POST /{id}/students/import, GET /{id}/students/export |
| Ability | GET /me, GET /student/{id} |
| Config | GET /ai, PUT /ai, POST /ai/test |

## 部署调试记录
| 问题 | 原因 | 解决 |
|------|------|------|
| 镜像 tag 大写 | github.repository 含 Y | 硬编码小写 |
| GHCR 401 | 默认私有 | 改为 Public |
| SQLite 连接失败 | 相对路径 + 无 data 目录 | 绝对路径 + mkdir |
| bcrypt 不兼容 | passlib 兼容新版 bcrypt | 锁定 bcrypt==4.0.1 |
| Dockerfile 合并冲突 | GitHub 网页编辑冲突 | 本地清理重推 |
| Git push 不稳定 | GFW 封 HTTPS | SSH Key 永久修复 |
| 图片 OCR 不匹配 | 无 OCR 引擎 | 改用 GLM-4V 视觉模型 |
| 学生端轮询失效 | useEffect 闭包旧值 | 用 ref + 独立轮询函数 |
