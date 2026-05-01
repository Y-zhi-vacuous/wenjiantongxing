"""
模型路由器 - 管理本地/云端模型的调度
支持：智谱 GLM / OpenAI / DeepSeek / Claude / Ollama
"""
import httpx
from app.models.ai_config import AIConfig


async def test_connection(config: AIConfig) -> bool:
    """测试 AI 连接是否可用"""
    try:
        if config.provider == "ollama":
            async with httpx.AsyncClient() as client:
                resp = await client.get("http://localhost:11434/api/tags", timeout=5)
                return resp.status_code == 200
        elif config.provider == "zhipu":
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                    json={"model": config.model_name, "messages": [{"role": "user", "content": "hi"}]},
                    headers={"Authorization": f"Bearer {config.api_key_encrypted}"},
                )
                return resp.status_code == 200
        else:
            return bool(config.api_key_encrypted)
    except Exception:
        return False
