from typing import Any
from pydantic import BaseModel, create_model

_TYPE_MAP = {
    "string": str,
    "integer": int,
    "object": dict,
    "boolean": bool,
    "number": float,
}


def _schema_to_pydantic(name: str, schema: dict[str, Any]) -> type[BaseModel]:
    """Build a Pydantic BaseModel from a JSON Schema object definition."""
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    fields: dict[str, Any] = {}
    for field_name, field_schema in properties.items():
        python_type = _TYPE_MAP.get(field_schema.get("type", "string"), str)
        if field_name in required:
            fields[field_name] = (python_type, ...)
        else:
            fields[field_name] = (python_type | None, None)
    return create_model(f"{name.title().replace('_', '')}Args", **fields)
