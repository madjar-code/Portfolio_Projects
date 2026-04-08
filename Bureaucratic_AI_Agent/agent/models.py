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


class ValidationIssue(BaseModel):
    field: str
    detail: str
    severity: str  # "critical" | "warning" | "info"


class AIReportPayload(BaseModel):
    application_id: str
    decision: str                        # "ACCEPT" | "REJECT" | "ERROR"
    confidence_score: float              # 0.0 – 1.0
    extracted_data: dict[str, Any]       # key-value pairs from document/form
    issues_found: list[ValidationIssue]
    recommendations: str | None = None
    processing_time_seconds: int
    ai_model_used: str
    prompt_version: str = "unknown"
