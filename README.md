# 文鉴同行

深圳中考 AI 作文智能批改平台。支持 **Web 访问**，让 AI 帮助初中生提升写作水平。

## 公网地址

🔗 **`https://wppyqjhwlqso.usw-1.sealos.app`**

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 18 + TypeScript + Vite + Tailwind CSS |
| 后端 | FastAPI + SQLAlchemy + SQLite |
| AI 批改 | 智谱 GLM-4 |
| 图片 OCR | 智谱 GLM-4V |
| 部署 | GitHub Actions → GHCR → Sealos |

## 快速启动 (本地开发)

```bash
# 后端
cd backend && pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend && npm install && npm run dev
```

## 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 教师 | teacher1 | test123 |
| 学生 | student1 | test123 |

## 功能

### 学生端
- 选题写作（在线/文件上传/拍照上传 → GLM-4V OCR）
- AI 批改报告（评分 + 逐段点评 + 总评 + 提升建议）
- 写作能力画像（四维能力 + 历史趋势 + 优劣势 + AI 计划）
- 修改密码 + AI 模型配置

### 教师端
- 班级管理 + 学生能力详情查看
- xlsx 批量导入/导出学生账号
- 题库管理（8 道深圳中考真题 + 自定义）
- 实名注册
