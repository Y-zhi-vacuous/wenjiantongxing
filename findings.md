# Findings

## 当前状态
- 应用名: 文鉴同行
- 本地开发: `localhost:8000` (后端) + `localhost:5173` (前端)
- Docker 镜像: `ghcr.io/y-zhi-vacuous/wenjiantongxing:latest` (自动构建)
- Sealos 公网: `https://wppyqjhwlqso.usw-1.sealos.app` (部署中，503 调试)
- APK: Capacitor 项目已初始化，待构建

## 技术栈
- 前端: React 18 + TypeScript + Vite + Tailwind CSS + Capacitor
- 后端: FastAPI + SQLAlchemy + SQLite/PostgreSQL
- AI: 智谱 GLM-4 (API Key 已配置)
- 部署: GitHub Actions → GHCR → Sealos
- 移动端: Capacitor Android

## 深圳中考标准
- 字数: 600-900 字
- 文体: 除诗歌外不限
- 评分: 45 分 (含书写 3 分)
- 规则: 匿名 (XXX 代替)、不得抄袭套作
- 题库: 8 道真题 (2017-2024) + 2 道模拟题

## API Endpoints
| Module | Key Endpoints |
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
| 镜像 tag 大写 | `github.repository` 含大写 Y | 硬编码全小写 |
| GHCR 401 | 包默认私有 | 改为 Public |
| Sealos 503 | 表未创建 + 数据目录缺失 | seed.py 加 create_all + Dockerfile 加 mkdir |
| Git push 失败 | GFW 封 git 协议 | GitHub 网页直接编辑文件 |
| Docker build 慢 | 每次构建都 npm ci + pip install | GitHub Actions 缓存 (后续优化) |
