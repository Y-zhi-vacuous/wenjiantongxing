import io
import base64

from app.config import get_settings


def parse_file_content(content_bytes: bytes, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext in ("docx", "doc"):
        return _parse_docx(content_bytes)
    elif ext == "pdf":
        return _parse_pdf(content_bytes)
    elif ext in ("png", "jpg", "jpeg", "gif", "bmp", "webp"):
        return _parse_image_sync(content_bytes)
    else:
        return content_bytes.decode("utf-8", errors="replace")


def parse_image_to_text(image_bytes: bytes) -> str:
    return _parse_image_sync(image_bytes)


async def parse_image_to_text_async(image_bytes: bytes, student_id: int = 0) -> str:
    """v2.0: 异步 OCR —— 使用学生 OCRConfig"""
    return await _parse_image_async(image_bytes, student_id=student_id)


def _parse_docx(content_bytes: bytes) -> str:
    try:
        from docx import Document
        doc = Document(io.BytesIO(content_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception:
        return content_bytes.decode("utf-8", errors="replace")


def _parse_pdf(content_bytes: bytes) -> str:
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        return "\n".join(text_parts)
    except Exception:
        return content_bytes.decode("utf-8", errors="replace")


def _compress_if_needed(content_bytes: bytes) -> bytes:
    if len(content_bytes) > 500_000:
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(content_bytes))
            w, h = img.size
            img = img.resize((w // 2, h // 2))
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=60)
            print(f"[OCR] 图片压缩: {len(content_bytes)} → {buf.tell()} bytes")
            return buf.getvalue()
        except Exception as e:
            print(f"[OCR] 压缩失败: {e}")
    return content_bytes


async def _parse_image_async(content_bytes: bytes, student_id: int = 0) -> str:
    """v2.0: 异步 OCR —— 优先使用学生 OCRConfig"""
    settings = get_settings()
    api_key = settings.AI_API_KEY or ""
    ocr_model = getattr(settings, 'AI_OCR_MODEL', None) or "glm-4.1v-thinking-flash"
    ocr_base_url = None

    # v2.0: 尝试读取学生 OCR 配置
    if student_id > 0:
        try:
            from app.db import async_session
            from app.models.ocr_config import OCRConfig
            async with async_session() as db:
                config_result = await db.execute(
                    __import__('sqlalchemy').select(OCRConfig).where(OCRConfig.user_id == student_id)
                )
                ocr_config = config_result.scalar_one_or_none()
                if ocr_config and ocr_config.is_active:
                    if ocr_config.model_name:
                        ocr_model = ocr_config.model_name
                    if ocr_config.api_key_encrypted:
                        api_key = ocr_config.api_key_encrypted
                    if ocr_config.base_url:
                        ocr_base_url = ocr_config.base_url
        except Exception as e:
            print(f"[OCR] 读取学生配置失败: {e}")

    content_bytes = _compress_if_needed(content_bytes)
    img_b64 = base64.b64encode(content_bytes).decode()
    print(f"[OCR] 模型={ocr_model} 图片base64={len(img_b64)}字节")

    import asyncio as aio
    import httpx

    models_to_try = [ocr_model, "glm-4v"]
    tried = set()
    last_error = ""

    for model in models_to_try:
        if model in tried:
            continue
        tried.add(model)

        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=90) as client:
                    payload = {
                        "model": model,
                        "messages": [{"role": "user", "content": [
                            {"type": "text", "text": "请识别这张手写作文图片中的所有文字，逐字逐句输出，保留原文段落格式，不要添加任何解释或修改。"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                        ]}],
                        "temperature": 0.1,
                        "max_tokens": 4096,
                    }
                    if "thinking" in model:
                        payload["thinking"] = {"type": "disabled"}

                    resp = await client.post(
                        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                        json=payload,
                        headers={"Authorization": f"Bearer {api_key}"},
                    )
                    data = resp.json()

                    if "choices" in data:
                        msg = data["choices"][0]["message"]
                        text = (msg.get("content") or "").strip()
                        if not text:
                            text = msg.get("reasoning_content", "").strip()
                        if len(text) > 20:
                            print(f"[OCR] 成功 模型={model} {len(text)}字")
                            return text
                        print(f"[OCR] {model} 输出过短({len(text)}字)，重试...")

                    elif "error" in data:
                        err_msg = data["error"].get("message", "")
                        last_error = err_msg
                        if "访问量过大" in err_msg or "rate" in err_msg.lower() or "限流" in err_msg:
                            wait = (attempt + 1) * 4
                            print(f"[OCR] {model} 限流，{wait}s后重试(第{attempt+1}次)...")
                            await aio.sleep(wait)
                            continue
                        else:
                            print(f"[OCR] {model} 错误: {err_msg}，换模型")
                            break
            except Exception as e:
                print(f"[OCR] {model} 异常: {e}")
                await aio.sleep(2)

    return f"[OCR失败: {last_error or '所有模型均无法识别，请稍后重试'}]"


def _parse_image_sync(content_bytes: bytes) -> str:
    """同步 OCR —— 非 async 上下文中的降级方案"""
    try:
        import asyncio
        import concurrent.futures
        loop = asyncio.get_event_loop()
        if loop.is_running():
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(lambda: asyncio.run(_parse_image_async(content_bytes)))
                return future.result(timeout=90)
        return asyncio.run(_parse_image_async(content_bytes))
    except Exception as e:
        print(f"[OCR] 同步异常: {e}")
        return _parse_image_local(content_bytes)


def _parse_image_local(content_bytes: bytes) -> str:
    """本地 OCR 降级"""
    try:
        import subprocess, tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(content_bytes)
            tmp_path = f.name
        result = subprocess.run(
            ["tesseract", tmp_path, "stdout", "-l", "chi_sim"],
            capture_output=True, text=True, timeout=30
        )
        os.unlink(tmp_path)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    try:
        from PIL import Image
        import pytesseract
        img = Image.open(io.BytesIO(content_bytes))
        text = pytesseract.image_to_string(img, lang="chi_sim")
        if text.strip():
            return text.strip()
    except Exception:
        pass
    return f"[手写作文 — OCR 未识别成功，请检查图片清晰度]\n图片大小: {len(content_bytes)} bytes"
