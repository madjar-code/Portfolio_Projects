import os
import random
import string
from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models import Manager

from common.mixins.managers import SoftDeletionManager
from common.mixins.models import BaseModel, TimeStampModel, UUIDModel

from .constants import ApplicationStatus, DocumentFormat, ProcedureType


def _generate_application_number() -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"APP-{date_str}-{suffix}"


def _document_upload_to(instance, filename: str) -> str:
    return f"documents/{instance.application_id}/{filename}"


class Application(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="applications",
    )
    procedure = models.CharField(max_length=30, choices=ProcedureType.choices)
    application_number = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.DRAFT,
    )
    form_data = models.JSONField(default=dict, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    objects = Manager()
    active_objects = SoftDeletionManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["procedure"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["submitted_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.application_number:
            self.application_number = _generate_application_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.application_number


class Document(BaseModel):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="documents",
    )
    file = models.FileField(upload_to=_document_upload_to)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    file_format = models.CharField(max_length=10, choices=DocumentFormat.choices, blank=True)

    objects = Manager()
    active_objects = SoftDeletionManager()

    class Meta:
        indexes = [
            models.Index(fields=["application"]),
            models.Index(fields=["user"]),
            models.Index(fields=["created_at"]),
        ]

    def save(self, *args, **kwargs):
        if self.file and not self.file_name:
            self.file_name = os.path.basename(self.file.name)
            self.file_size = self.file.size
            ext = os.path.splitext(self.file.name)[1].upper().lstrip(".")
            self.file_format = ext if ext in DocumentFormat.values else ""
        super().save(*args, **kwargs)

    def __str__(self):
        return self.file_name


class AIDecision(models.TextChoices):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    ERROR  = "ERROR"


class AIReport(UUIDModel, TimeStampModel):
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name="report",
    )
    decision = models.CharField(max_length=10, choices=AIDecision.choices, default=AIDecision.REJECT)
    confidence_score = models.FloatField(null=True, blank=True)
    extracted_data = models.JSONField(default=dict)
    issues_found = models.JSONField(default=list)
    recommendations = models.TextField(blank=True)
    processing_time_seconds = models.PositiveIntegerField(null=True, blank=True)
    ai_model_used = models.CharField(max_length=50, blank=True)
    prompt_version = models.CharField(max_length=50, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Report for {self.application}"
