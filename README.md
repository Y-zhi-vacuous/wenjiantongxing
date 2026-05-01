# 文鉴同行

深圳中考 AI 作文智能批改平台。支持 **Web 访问** 和 **Android APK 安装**。

## 已部署地址

- 🔗 **Web**: `https://wppyqjhwlqso.usw-1.sealos.app` (Sealos 免费托管)
- 🔗 **API 文档**: `https://wppyqjhwlqso.usw-1.sealos.app/docs`

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 18 + TypeScript + Vite + Tailwind CSS + Capacitor |
| 后端 | FastAPI + SQLAlchemy (SQLite/PostgreSQL) |
| AI | 智谱 GLM-4 API |
| 部署 | GitHub Actions → GHCR → Sealos |
| 移动端 | Capacitor Android APK |

## 快速启动 (本地开发)

```bash
# 后端
cd backend
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev
```

## 测试账号

| 角色 | 用户名 | 密码 | 备注 |
|------|--------|------|------|
| 教师 | teacher1 | test123 | 实名: 李明远 |
| 学生 | student1 | test123 | 九(3)班 |

## 功能

### 学生端
- 选题写作（在线/文件上传/拍照上传）
- AI 批改报告（评分 + 逐段点评 + 总评 + 建议）
- 写作能力画像（四维能力 + 趋势 + 优劣势）
- 修改密码 + AI 配置

### 教师端
- 班级管理 + 学生能力查看
- xlsx 批量导入/导出学生
- 题库管理（8 道深圳中考真题）
- 实名注册
