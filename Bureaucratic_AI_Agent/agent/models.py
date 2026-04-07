from typing import Any
from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    file_name: str
    file_url: str
    file_format: str
    file_size: int | None = None


class TaskMessage(BaseModel):
    application_id: str
    procedure: str
    form_data: dict[str, Any]
    document: DocumentMetadata | None = None


class AIReportPayload(BaseModel):
    application_id: str
    decision: str                        # "ACCEPT" or "REJECT"
    validation_result: dict[str, Any]
    extracted_data: dict[str, Any]
    issues_found: list[dict[str, Any]]
    recommendations: str
    processing_time_seconds: int
    ai_model_used: str
    prompt_version: str = "unknown"

