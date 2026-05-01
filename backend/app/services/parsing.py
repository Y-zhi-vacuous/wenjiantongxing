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
        return _parse_image(content_bytes)
    else:
        return content_bytes.decode("utf-8", errors="replace")


def parse_image_to_text(image_bytes: bytes, user_id: int = 0) -> str:
    return _parse_image(image_bytes, user_id)


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


def _parse_image(content_bytes: bytes, user_id: int = 0) -> str:
    """使用智谱视觉模型进行 OCR 识别"""
    settings = get_settings()
    api_key = settings.AI_API_KEY or "08291980aa0d44928db4cf142733edc4.Q41wSJGtwIy2IYmc"
    ocr_model = getattr(settings, 'AI_OCR_MODEL', None) or "glm-4.1v-thinking-flash"

    import httpx
    import asyncio

    async def _ocr():
        img_b64 = base64.b64encode(content_bytes).decode()
        async with httpx.AsyncClient(timeout=60) as client:
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
                return data["choices"][0]["message"]["content"].strip()
            return f"[OCR失败: {data.get('error',{}).get('message','未知错误')}]"

    try:
        return asyncio.run(_ocr())
    except Exception as e:
        # 降级：尝试本地 OCR
        return _parse_image_local(content_bytes)


def _parse_image_local(content_bytes: bytes) -> str:
    """本地 OCR 降级方案"""
    # 尝试 tesseract
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

    # 尝试 pytesseract
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
