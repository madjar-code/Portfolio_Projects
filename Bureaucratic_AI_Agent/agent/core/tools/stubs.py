from core.tools import Tool, ToolRegistry


async def _read_document_page(page_number: int) -> str:
    return (
        f"[stub] Page {page_number}: PASSPORT\n"
        "Full Name: Ivan Ivanov\nDate of Birth: 1990-01-13\n"
        "Document No: A1234567\nExpiry: 2030-01-01"
    )


async def _ocr_document_region(page: int, x: int, y: int, width: int, height: int) -> str:
    return f"[stub] OCR region (page={page}, x={x}, y={y}, w={width}, h={height}): Ivan Ivanov"


async def _extract_field_from_document(field_name: str) -> str:
    data = {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "date_of_birth": "1990-01-13",
        "document_number": "A1234567",
        "expiry_date": "2030-01-01",
    }
    return data.get(field_name, f"[stub] field '{field_name}' not found")


async def _call_external_api(endpoint: str, params: dict) -> str:
    return f"[stub] {endpoint} → 200 OK {{'valid': true}}"


_TOOLS = [
    Tool(
        name="read_document_page",
        description="Read a full page of the submitted document and return its text content.",
        parameters={
            "type": "object",
            "properties": {
                "page_number": {"type": "integer", "description": "1-based page number"},
            },
            "required": ["page_number"],
        },
        fn=_read_document_page,
    ),
    Tool(
        name="ocr_document_region",
        description="Run OCR on a specific rectangular region of a document page.",
        parameters={
            "type": "object",
            "properties": {
                "page": {"type": "integer"},
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "width": {"type": "integer"},
                "height": {"type": "integer"},
            },
            "required": ["page", "x", "y", "width", "height"],
        },
        fn=_ocr_document_region,
    ),
    Tool(
        name="extract_field_from_document",
        description="Extract a named field (e.g. first_name, date_of_birth) from the document.",
        parameters={
            "type": "object",
            "properties": {
                "field_name": {"type": "string"},
            },
            "required": ["field_name"],
        },
        fn=_extract_field_from_document,
    ),
    Tool(
        name="call_external_api",
        description="Call a mock external government API to cross-validate applicant data.",
        parameters={
            "type": "object",
            "properties": {
                "endpoint": {"type": "string"},
                "params": {"type": "object"},
            },
            "required": ["endpoint", "params"],
        },
        fn=_call_external_api,
    ),
]


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    for tool in _TOOLS:
        registry.register(tool)
    return registry
