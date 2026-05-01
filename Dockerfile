  FROM node:20-alpine AS frontend-build
  WORKDIR /app/frontend
  COPY frontend/package.json frontend/package-lock.json ./
  RUN npm ci
  COPY frontend/ ./
  RUN npm run build

  FROM python:3.12-slim
  WORKDIR /app

  RUN apt-get update && apt-get install -y --no-install-recommends \
      libpq-dev gcc curl && rm -rf /var/lib/apt/lists/*

  COPY backend/requirements.txt ./
  RUN pip install --no-cache-dir -r requirements.txt

  COPY backend/ ./
  COPY --from=frontend-build /app/frontend/dist ./frontend/dist

  RUN mkdir -p /app/data

  ENV FRONTEND_DIR=./frontend/dist
  ENV PORT=8080
  ENV DEBUG=false
  ENV DATABASE_URL=sqlite+aiosqlite:////app/data/essay_app.db

  EXPOSE 8080

  CMD python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port 8080 --proxy-headers
