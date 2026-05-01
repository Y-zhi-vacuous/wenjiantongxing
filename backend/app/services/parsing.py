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


async def parse_image_to_text_async(image_bytes: bytes) -> str:
    """异步 OCR —— 在 FastAPI async endpoint 中直接调用"""
    return await _parse_image_async(image_bytes)


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


async def _parse_image_async(content_bytes: bytes) -> str:
    """异步 OCR —— 智谱 GLM-4V"""
    settings = get_settings()
    api_key = settings.AI_API_KEY or "08291980aa0d44928db4cf142733edc4.Q41wSJGtwIy2IYmc"
    ocr_model = getattr(settings, 'AI_OCR_MODEL', None) or "glm-4.1v-thinking-flash"

    content_bytes = _compress_if_needed(content_bytes)
    img_b64 = base64.b64encode(content_bytes).decode()
    print(f"[OCR] 模型={ocr_model} 图片base64={len(img_b64)}字节")

    import httpx
    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            json={
                "model": ocr_model,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请识别这张手写作文图片中的所有文字，逐字逐句输出，保留原文段落格式，不要添加任何解释或修改。"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                    ]
                }],
                "temperature": 0.1,
                "max_tokens": 4096,
            },
            headers={"Authorization": f"Bearer {api_key}"},
        )
        data = resp.json()
        if "choices" in data:
            text = data["choices"][0]["message"]["content"].strip()
            print(f"[OCR] 成功，{len(text)} 字")
            return text
        print(f"[OCR] API错误: {data}")
        return f"[OCR失败: {data.get('error',{}).get('message','未知错误')}]"


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
