import io
import base64


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


def parse_image_to_text(image_bytes: bytes) -> str:
    """OCR 图片文字提取"""
    return _parse_image(image_bytes)


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


def _parse_image(content_bytes: bytes) -> str:
    """图片 OCR — 尝试多种引擎，降级返回提示"""
    # 尝试 Tesseract OCR
    try:
        import subprocess
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(content_bytes)
            tmp_path = f.name
        result = subprocess.run(
            ["tesseract", tmp_path, "stdout", "-l", "chi_sim"],
            capture_output=True, text=True, timeout=30
        )
        import os
        os.unlink(tmp_path)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass

    # 尝试使用 pytesseract
    try:
        from PIL import Image
        import pytesseract
        img = Image.open(io.BytesIO(content_bytes))
        text = pytesseract.image_to_string(img, lang="chi_sim")
        if text.strip():
            return text.strip()
    except Exception:
        pass

    # 降级：返回提示 + base64 编码的前 200 字符用于人工查看
    return f"[图片作文 — 未检测到 OCR 引擎，请安装 Tesseract 或 pytesseract]\n图片大小: {len(content_bytes)} bytes"

