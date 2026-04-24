import asyncio
import io
import logging

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)

# Extend with additional language codes as needed (e.g. "rus+eng+deu").
_TESSERACT_LANG = "rus+eng"
# Tesseract PSM 6: assume a single uniform block of text.
_TESSERACT_CONFIG = "--psm 6"
# Scale factor: upsampling improves recognition of thin characters (e.g. "I").
_SCALE = 2


def _preprocess(image: Image.Image) -> Image.Image:
    image = image.convert("L")  # grayscale
    w, h = image.size
    image = image.resize((w * _SCALE, h * _SCALE), Image.LANCZOS)
    image = ImageEnhance.Contrast(image).enhance(2.0)
    image = image.filter(ImageFilter.SHARPEN)
    return image


async def tesseract_extract(image_bytes: bytes, mime_type: str, prompt: str) -> str:
    """
    Extract text from image bytes using Tesseract OCR.

    Drop-in replacement for vision_extract. The prompt parameter is accepted
    for interface compatibility but is not used by Tesseract.
    """
    image = Image.open(io.BytesIO(image_bytes))
    image = _preprocess(image)
    logger.debug("tesseract_extract: mime=%s bytes=%d", mime_type, len(image_bytes))
    text = await asyncio.to_thread(
        pytesseract.image_to_string, image, lang=_TESSERACT_LANG, config=_TESSERACT_CONFIG
    )
    return text.strip()
