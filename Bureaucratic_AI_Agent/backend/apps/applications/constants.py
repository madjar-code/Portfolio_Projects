from django.db import models


class ProcedureType(models.TextChoices):
    PASSPORT_MD = "passport_md", "Passport Application MD"
    BUSINESS_REG = "business_reg", "Individual Entrepreneur Registration"


class ApplicationStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SUBMITTED = "SUBMITTED", "Under Review"
    PROCESSING = "PROCESSING", "Processing"
    ADDITIONAL_INFO_REQUIRED = "ADDITIONAL_INFO_REQUIRED", "Additional Info Required"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    CANCELLED = "CANCELLED", "Cancelled"
    FAILED = "FAILED", "Failed"


class DocumentFormat(models.TextChoices):
    PDF = "PDF", "PDF"
    DOCX = "DOCX", "DOCX"
    JPG = "JPG", "JPG"
    PNG = "PNG", "PNG"


PROCEDURES: dict[str, dict] = {
    ProcedureType.PASSPORT_MD: {
        "name": "Passport Application MD",
        "description": "Application for a new passport in Moldova.",
        "required_document_formats": ["PDF", "JPG", "PNG"],
        "instruction_file": "procedures/passport_md.md",
    },
    ProcedureType.BUSINESS_REG: {
        "name": "Individual Entrepreneur Registration",
        "description": "Registration of an individual entrepreneur.",
        "required_document_formats": ["PDF", "DOCX"],
        "instruction_file": "procedures/business_reg.md",
    },
}
