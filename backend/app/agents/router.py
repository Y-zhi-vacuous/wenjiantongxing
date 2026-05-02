"""
统一 LLM 路由层 — v2.0

支持 6 个提供商: Zhipu / OpenAI / DeepSeek / Claude / Ollama / vLLM
统一接口 call_llm() 处理所有 LLM 调用，自动转换消息格式。
"""
import httpx
from app.models.grading_config import GradingProvider


PROVIDER_ENDPOINTS = {
    "zhipu": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    "openai": "https://api.openai.com/v1/chat/completions",
    "deepseek": "https://api.deepseek.com/v1/chat/completions",
    "claude": "https://api.anthropic.com/v1/messages",
}


async def call_llm(
    provider: str,
    model: str,
    messages: list[dict],
    api_key: str,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    base_url: str | None = None,
    local_endpoint_url: str | None = None,
    timeout: int = 90,
    retries: int = 2,
) -> dict:
    """
    统一 LLM 调用接口。

    Returns:
        {"content": str, "model": str, "usage": dict | None}
    Raises:
        ValueError: 不支持的 provider
        httpx.HTTPError: 网络错误
        RuntimeError: API 返回错误
    """
    if provider in ("zhipu", "openai", "deepseek"):
        return await _call_openai_compatible(
            url=PROVIDER_ENDPOINTS[provider],
            model=model, messages=messages, api_key=api_key,
            temperature=temperature, max_tokens=max_tokens,
            timeout=timeout, retries=retries,
        )
    elif provider == "claude":
        return await _call_claude(
            model=model, messages=messages, api_key=api_key,
            temperature=temperature, max_tokens=max_tokens,
            timeout=timeout,
        )
    elif provider == "ollama":
        url = local_endpoint_url or "http://localhost:11434"
        return await _call_ollama(
            url=url, model=model, messages=messages,
            temperature=temperature, max_tokens=max_tokens,
            timeout=timeout,
        )
    elif provider == "vllm":
        url = local_endpoint_url or "http://localhost:8000"
        return await _call_openai_compatible(
            url=f"{url.rstrip('/')}/v1/chat/completions",
            model=model, messages=messages, api_key=api_key or "not-needed",
            temperature=temperature, max_tokens=max_tokens,
            timeout=timeout, retries=retries,
        )
    else:
        raise ValueError(f"不支持的 AI 提供商: {provider}")


async def _call_openai_compatible(
    url: str, model: str, messages: list[dict], api_key: str,
    temperature: float, max_tokens: int, timeout: int, retries: int,
) -> dict:
    """OpenAI-compatible API (Zhipu/OpenAI/DeepSeek/vLLM)"""
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    last_error = None
    for attempt in range(retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 429 and attempt < retries:
                    import asyncio
                    wait = (attempt + 1) * 4
                    print(f"[LLM] 限流 {url}, {wait}s后重试(第{attempt+1}次)")
                    await asyncio.sleep(wait)
                    continue
                data = resp.json()
                if "choices" in data and data["choices"]:
                    choice = data["choices"][0]
                    content = choice.get("message", {}).get("content", "")
                    return {
                        "content": content.strip(),
                        "model": data.get("model", model),
                        "usage": data.get("usage"),
                    }
                if "error" in data:
                    last_error = data["error"].get("message", str(data))
                    break
        except httpx.TimeoutException:
            last_error = f"请求超时 ({timeout}s)"
        except Exception as e:
            last_error = str(e)
            if attempt < retries:
                import asyncio
                await asyncio.sleep(2)

    raise RuntimeError(f"LLM 调用失败: {last_error or '未知错误'}")


async def _call_claude(
    model: str, messages: list[dict], api_key: str,
    temperature: float, max_tokens: int, timeout: int,
) -> dict:
    """Anthropic Claude API (非标准消息格式)"""
    # 提取 system 消息和 user 消息
    system_msg = ""
    user_messages = []
    for m in messages:
        if m["role"] == "system":
            system_msg = m["content"]
        else:
            user_messages.append(m)

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": user_messages,
    }
    if system_msg:
        payload["system"] = system_msg

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            json=payload, headers=headers,
        )
        if resp.status_code != 200:
            data = resp.json()
            raise RuntimeError(f"Claude API 错误: {data.get('error', {}).get('message', str(data))}")

        data = resp.json()
        content = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                content += block["text"]

        return {
            "content": content.strip(),
            "model": data.get("model", model),
            "usage": data.get("usage"),
        }


async def _call_ollama(
    url: str, model: str, messages: list[dict],
    temperature: float, max_tokens: int, timeout: int,
) -> dict:
    """Ollama 本地 API"""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(f"{url.rstrip('/')}/api/chat", json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"Ollama 错误: {resp.text}")

        data = resp.json()
        return {
            "content": data.get("message", {}).get("content", "").strip(),
            "model": data.get("model", model),
            "usage": {
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
            },
        }


async def test_connection(
    provider: str,
    api_key: str = "",
    model: str = "",
    base_url: str | None = None,
    local_endpoint_url: str | None = None,
) -> bool:
    """测试 AI 连接"""
    try:
        if provider == "ollama":
            url = local_endpoint_url or "http://localhost:11434"
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{url.rstrip('/')}/api/tags")
                return resp.status_code == 200
        elif provider == "vllm":
            url = local_endpoint_url or "http://localhost:8000"
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{url.rstrip('/')}/v1/models")
                return resp.status_code == 200
        elif provider == "claude":
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    json={"model": model or "claude-sonnet-4-6", "max_tokens": 10, "messages": [{"role": "user", "content": "hi"}]},
                    headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
                )
                return resp.status_code == 200
        elif provider in ("zhipu", "openai", "deepseek"):
            url = PROVIDER_ENDPOINTS[provider]
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    url,
                    json={"model": model or "gpt-3.5-turbo", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                return resp.status_code == 200
        else:
            return bool(api_key)
    except Exception:
        return False
