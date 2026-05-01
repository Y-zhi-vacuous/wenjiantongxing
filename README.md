# 文鉴同行

深圳中考 AI 作文智能批改平台。支持 Web + Android APK。

## 公网

🔗 `https://wppyqjhwlqso.usw-1.sealos.app`

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 18 + TS + Vite + Tailwind + Capacitor |
| 后端 | FastAPI + SQLAlchemy + SQLite |
| AI 批改 | 智谱 GLM-4-Flash-250414 |
| 图片 OCR | glm-4.1v-thinking-flash → glm-4v 降级 |
| 部署 | GitHub Actions → GHCR → Sealos |

## 评分系统

| 维度 | 满分 |
|------|------|
| 立意 | 10 |
| 内容 | 15 |
| 语言 | 10 |
| 结构 | 5 |
| 文面 | 5 |
| **总分** | **45** |

切题判定直接影响评分上限：偏题≤29、离题≤10。

## 快速启动

```bash
cd backend && pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload --port 8000

cd frontend && npm install && npm run dev
```

## 测试账号

| 角色 | 用户 | 密码 |
|------|------|------|
| 教师 | teacher1 | test123 |
| 学生 | student1 | test123 |
