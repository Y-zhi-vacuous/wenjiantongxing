# Findings

## 当前状态
- 应用: 文鉴同行 v1.0
- 公网: `https://wppyqjhwlqso.usw-1.sealos.app`
- GitHub: `Y-zhi-vacuous/wenjiantongxing`

## 技术栈
- 前端: React 18 + TS + Vite + Tailwind + Capacitor 8
- 后端: FastAPI + SQLAlchemy + SQLite
- AI: 智谱 GLM-4-Flash-250414 (评分) + glm-4.1v-thinking-flash (OCR)
- 部署: GitHub Actions → GHCR → Sealos

## AI 评分系统

### 五项维度 (满分 45)
| 维度 | 满分 |
|------|------|
| 立意 | 10 |
| 内容 | 15 |
| 语言 | 10 |
| 结构 | 5 |
| 文面 | 5 |

### 切题硬限制 (后端强制)
| 判定 | 立意上限 | 总分上限 |
|------|---------|---------|
| 切题/基本切题 | 10 | 45 |
| 部分偏题 | 5 | 29 |
| 完全离题 | 2 | 10 |

### 字数限制
- <100字: ≤10分
- 100-300字: ≤29分
- 300-500字: ≤34分

## OCR
- 默认: glm-4.1v-thinking-flash (thinking: disabled)
- 降级: glm-4v (限流时自动切换)
- 重试: 3次，间隔 4/8/12s
- 图片 >500KB 自动压缩

## API Endpoints
| Module | Endpoints |
|--------|------|
| Auth | POST /register/teacher, /register/student, /login, PUT /password |
| Essays | POST /, /upload, /upload-image, /{id}/grade, /{id}/report |
| Topics | GET /, POST / |
| Classes | GET /, POST /, /{id}/students/template, /import, /export |
| Ability | GET /me, /student/{id} |
| Config | GET /ai, PUT /ai |

## 部署调试记录
| 问题 | 解决 |
|------|------|
| 镜像标签大写 | 硬编码小写 |
| GHCR 401 | 改 Public |
| SQLite 连接 | 绝对路径 + mkdir |
| bcrypt 不兼容 | bcrypt==4.0.1 |
| Git push 不稳定 | SSH Key |
| APK Java 版本 | Java 21 |
| APK 中文路径 | overridePathCheck |
| OCR event loop | 异步直接 await |
| OCR thinking 输出短 | thinking: disabled |
| OCR 限流 | 3次重试+降级 |
| 评分超满分 | 后端 clamp 硬限制 |
| 离题仍高分 | topic_match 强制上限 |
