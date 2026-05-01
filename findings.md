# Findings & Decisions

## Requirements (Current)
- 应用名称：文鉴同行
- 深圳中考初中生为目标用户
- 学生端 + 教师端双角色，教师实名注册
- 学生账号由教师统一创建（单个 + xlsx 批量导入），不可自主注册
- 学生登录后可在设置中修改密码
- 作文批改：在线写作 / 文件上传(doc/docx/pdf) / 手写拍照(image) → AI 批改 → 结构化报告
- 分项评分：内容(40%) + 语言(30%) + 结构(20%) + 卷面(10%)，对标深圳中考满分45分
- 写作要求：600-900字、除诗歌外文体不限、匿名规则(XXX代替)、不得抄袭套作
- AI 后端：混合方案，Mock 模式开发，UI 可配置
- 学生能力画像：每次批改后自动更新四维能力值 + 历史趋势 + 优劣势 + 改进计划
- 题库：8 道深圳中考真题(2017-2024) + 2 道模拟题，教师可自定义添加
- xlsx 批量导入导出学生信息
- 前端风格：Apple Native

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| FastAPI | 高性能异步 Python 框架 |
| React 18 + TypeScript + Vite | 现代化 SPA 开发 |
| SQLite (dev) / PostgreSQL (prod) | 零配置开发，生产迁移 |
| Tailwind CSS | 原子化 CSS，backdrop-blur 原生支持 |
| Mock Agent | 无需真实 API 即可全流程开发调试 |
| openpyxl | 纯 Python xlsx 处理 |
| JWT Query Param | 解决文件下载的认证问题 |

## Shenzhen Exam Requirements (Verified)
- 字数: 600-900字 (少写或多写均扣分)
- 文体: 除诗歌外不限，记叙文为主流
- 匿名: 不得出现真实校名、人名、地名，用XXX代替
- 诚信: 不得抄袭、套作
- 时间: 语文120分钟，作文建议45-50分钟
- 分值: 45分 (含书写分3分)
- 趋势: 以"我"为主体，成长类主题，全命题为主

## API Endpoints
| Module | Endpoints |
|--------|-----------|
| Auth | POST /register/teacher, POST /register/student, POST /login, GET /me, PUT /password |
| Essays | POST /, POST /upload, POST /upload-image, GET /, GET /{id}, GET /{id}/report, POST /{id}/grade |
| Topics | GET /, POST /, GET /{id} |
| Classes | GET /, POST /, GET /{id}, GET /{id}/students, POST /{id}/students |
| Students | GET /{id}/students/template, POST /{id}/students/import, GET /{id}/students/export |
| Ability | GET /me, GET /student/{id} |
| Config | GET /ai, PUT /ai, POST /ai/test |
