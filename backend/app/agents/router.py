"""
统一 LLM 路由层 — v2.0

支持 6 个提供商: Zhipu / OpenAI / DeepSeek / Claude / Ollama / vLLM
统一接口 call_llm() 处理所有 LLM 调用，自动转换消息格式。
"""
import json
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
                    msg = choice.get("message", {})
                    content = msg.get("content", "") or msg.get("reasoning_content", "")
                    if not content:
                        print(f"[LLM] 警告: API 返回空内容, choice keys={list(choice.keys())}, msg keys={list(msg.keys())}")
                        print(f"[LLM] 完整响应前500字: {json.dumps(data, ensure_ascii=False)[:500]}")
                    return {
                        "content": content.strip(),
                        "model": data.get("model", model),
                        "usage": data.get("usage"),
                    }
                if "error" in data:
                    last_error = data["error"].get("message", str(data))
                    print(f"[LLM] API 返回错误: {last_error}")
                    break
                # 既无 choices 也无 error — 记录完整响应
                print(f"[LLM] 意外的 API 响应: {json.dumps(data, ensure_ascii=False)[:500]}")
                last_error = f"API 返回异常: {json.dumps(data, ensure_ascii=False)[:200]}"
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
) -> tuple[bool, str]:
    """测试 AI 连接，返回 (是否成功, 详细信息)"""
    if not api_key and provider not in ("ollama", "vllm"):
        return False, "未配置 API Key"

    try:
        if provider == "ollama":
            url = local_endpoint_url or "http://localhost:11434"
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{url.rstrip('/')}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("name", "") for m in data.get("models", [])]
                    return True, f"连接成功，可用模型: {', '.join(models[:5])}"
                return False, f"Ollama 返回 {resp.status_code}: {resp.text[:100]}"

        elif provider == "vllm":
            url = local_endpoint_url or "http://localhost:8000"
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{url.rstrip('/')}/v1/models")
                if resp.status_code == 200:
                    return True, "vLLM 连接成功"
                return False, f"vLLM 返回 {resp.status_code}: {resp.text[:100]}"

        elif provider == "claude":
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    json={"model": model or "claude-sonnet-4-6", "max_tokens": 10, "messages": [{"role": "user", "content": "hi"}]},
                    headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
                )
                if resp.status_code == 200:
                    return True, "Claude API 连接成功"
                err = resp.json()
                msg = err.get("error", {}).get("message", resp.text[:100])
                return False, f"Claude API 错误: {msg}"

        elif provider in ("zhipu", "openai", "deepseek"):
            url = PROVIDER_ENDPOINTS[provider]
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    url,
                    json={"model": model or "gpt-3.5-turbo", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                if resp.status_code == 200:
                    return True, f"{provider} API 连接成功 (model: {model})"
                data = resp.json()
                if "error" in data:
                    msg = data["error"].get("message", str(data))
                    return False, f"API 返回错误: {msg}"
                return False, f"HTTP {resp.status_code}: {resp.text[:100]}"

        else:
            return bool(api_key), "已配置 API Key" if api_key else "未配置 API Key"

    except httpx.ConnectError:
        return False, f"无法连接到服务器，请检查端点地址"
    except httpx.TimeoutException:
        return False, "连接超时，请检查网络或服务器状态"
    except Exception as e:
        return False, f"连接失败: {str(e)[:100]}"
