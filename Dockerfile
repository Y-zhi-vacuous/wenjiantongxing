# 多阶段构建：前端编译 + 后端运行
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./

# 复制前端构建产物
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# 环境变量默认值
ENV FRONTEND_DIR=./frontend/dist
ENV PORT=8080
ENV DEBUG=false

EXPOSE 8080

# 启动：先初始化数据，再启动服务（带 proxy headers 支持反向代理）
CMD python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --proxy-headers
