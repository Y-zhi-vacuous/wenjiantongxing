#!/bin/bash
# 文鉴同行 - 一键部署脚本 (Sealos)
# 用法: bash deploy.sh

set -e
echo "=============================="
echo "  文鉴同行 - 部署到 Sealos"
echo "=============================="

# 1. 检查 Sealos CLI 是否安装
if ! command -v sealos &> /dev/null; then
    echo "[1/4] 安装 Sealos CLI..."
    curl -sfL https://sealos.run/install.sh | bash
    echo "Sealos CLI 安装完成"
else
    echo "[1/4] Sealos CLI 已安装"
fi

# 2. 登录 Sealos
echo "[2/4] 登录 Sealos..."
echo "请在浏览器中打开: https://sealos.run"
echo "登录后，在右上角头像 → API Keys → 创建 Token"
read -p "粘贴你的 Sealos Token: " SEALOS_TOKEN
sealos login --token "$SEALOS_TOKEN"

# 3. 创建数据库
echo "[3/4] 创建 PostgreSQL..."
sealos run labring/postgres:latest --name wenjiantongxing-db \
  -e POSTGRES_USER=wjt_user \
  -e POSTGRES_PASSWORD=wjt_pass_2026 \
  -e POSTGRES_DB=wenjiantongxing \
  --cpu 0.5 --memory 512Mi

echo "等待数据库启动..."
sleep 30

# 4. 构建并部署应用
echo "[4/4] 部署应用..."
DB_HOST=$(sealos get pod -l app=wenjiantongxing-db -o jsonpath='{.items[0].status.podIP}')
export DATABASE_URL="postgresql://wjt_user:wjt_pass_2026@${DB_HOST}:5432/wenjiantongxing"
export SECRET_KEY="wjt-prod-$(date +%s)"

sealos build -t wenjiantongxing:latest .
sealos run wenjiantongxing:latest --name wenjiantongxing \
  -e DATABASE_URL="$DATABASE_URL" \
  -e SECRET_KEY="$SECRET_KEY" \
  -e AI_PROVIDER="zhipu" \
  -e AI_MODEL="glm-4-flash" \
  -e AI_API_KEY="08291980aa0d44928db4cf142733edc4.Q41wSJGtwIy2IYmc" \
  -e CORS_ORIGINS="*" \
  --port 8080 --cpu 0.5 --memory 1Gi

echo ""
echo "=============================="
echo "  部署完成！"
echo "  访问地址: https://wenjiantongxing.sealos.run"
echo "=============================="
