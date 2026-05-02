# 文鉴同行

深圳中考 AI 作文批改平台。Web + Android APK。

🔗 `https://wppyqjhwlqso.usw-1.sealos.app`

## 技术

React 18 + FastAPI + SQLite + 智谱 GLM-4

## 评分 (五维 45 分)

| 立意 | 内容 | 语言 | 结构 | 文面 |
|------|------|------|------|------|
| 10 | 15 | 10 | 5 | 5 |

离题≤10 / 偏题≤29

## 快速启动

```bash
cd backend && pip install -r requirements.txt && python -m app.seed
uvicorn app.main:app --reload --port 8000
cd frontend && npm install && npm run dev
```

## 测试

teacher1 / student1 (test123)
