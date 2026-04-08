import base64
import logging
from langchain_core.messages import HumanMessage
from core.llm_registry import LLMRegistry

logger = logging.getLogger(__name__)

_VISION_MODEL = "gpt-4o-mini"


async def vision_extract(image_bytes: bytes, mime_type: str, prompt: str) -> str:
    """Send image bytes to OpenAI Vision and return extracted text."""
    b64 = base64.b64encode(image_bytes).decode()
    llm = LLMRegistry.get(_VISION_MODEL)
    msg = HumanMessage(content=[
        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
        {"type": "text", "text": prompt},
    ])
    logger.debug("Vision extract: model=%s mime=%s bytes=%d", _VISION_MODEL, mime_type, len(image_bytes))
    response = await llm.ainvoke([msg])
    return response.content
