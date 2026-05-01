FROM python:3.12-slim
WORKDIR /app
RUN pip install fastapi uvicorn
COPY backend/app/config.py ./app/
RUN mkdir -p /app/app && echo 'from fastapi import FastAPI; app=FastAPI(); [app.get("/api/health")(lambda: {"status":"ok"}); exec("import uvicorn; uvicorn.run(app,host=\"0.0.0.0\",port=8080)")]' > /app/app/main.py
ENV PORT=8080
EXPOSE 8080
CMD python -c "from app.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8080)"
