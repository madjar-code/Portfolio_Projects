from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import serializers, status

from apps.applications.models import Application, AIReport, AIDecision
from apps.applications.constants import ApplicationStatus
from apps.applications.metrics import (
    application_confidence_score,
    application_processing_duration_seconds,
    applications_decided_total,
)

from config.redis_client import publish_sse_event
from config.hmac_auth import verify_hmac_signature


class AIReportCallbackSerializer(serializers.Serializer):
    application_id = serializers.UUIDField()
    decision = serializers.ChoiceField(choices=AIDecision.choices)
    confidence_score = serializers.FloatField(min_value=0.0, max_value=1.0, required=False, allow_null=True)
    extracted_data = serializers.JSONField(default=dict)
    issues_found = serializers.JSONField(default=list)
    recommendations = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    processing_time_seconds = serializers.IntegerField(min_value=0)
    ai_model_used = serializers.CharField()
    prompt_version = serializers.CharField(required=False, allow_blank=True, default="unknown")


_DECISION_TO_STATUS = {
    AIDecision.ACCEPT: ApplicationStatus.APPROVED,
    AIDecision.REJECT: ApplicationStatus.REJECTED,
    AIDecision.ERROR: ApplicationStatus.FAILED,
}


class CallbackView(APIView):
    """
    Receives AI agent processing result.
    Authenticated by HMAC-SHA256 signature (not JWT — agent has no user account).
    Headers: X-Timestamp (unix seconds), X-Signature (hex HMAC-SHA256).
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        body = request.body
        timestamp = request.headers.get("X-Timestamp", "")
        signature = request.headers.get("X-Signature", "")
        if not verify_hmac_signature(body, timestamp, signature):
            return Response(
                {"error": {"message": "Invalid or missing signature."}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = AIReportCallbackSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data

        try:
            application = Application.objects.select_related("user").get(id=data["application_id"])
        except Application.DoesNotExist:
            return Response(
                {"error": {"message": "Application not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        new_status = _DECISION_TO_STATUS[data["decision"]]

        with transaction.atomic():
            AIReport.objects.update_or_create(
                application=application,
                defaults={
                    "decision": data["decision"],
                    "confidence_score": data.get("confidence_score"),
                    "extracted_data": data["extracted_data"],
                    "issues_found": data["issues_found"],
                    "recommendations": data.get("recommendations") or "",
                    "processing_time_seconds": data["processing_time_seconds"],
                    "ai_model_used": data["ai_model_used"],
                    "prompt_version": data["prompt_version"],
                },
            )
            application.status = new_status
            application.save(update_fields=["status", "updated_at"])
            publish_sse_event(
                user_id=str(application.user_id),
                application_id=str(application.id),
                status=new_status,
                application_number=application.application_number,
            )

        labels = {"procedure": application.procedure, "decision": data["decision"]}
        applications_decided_total.labels(**labels).inc()

        confidence = data.get("confidence_score")
        if confidence is not None:
            application_confidence_score.labels(**labels).observe(confidence)

        if application.submitted_at is not None:
            elapsed = (timezone.now() - application.submitted_at).total_seconds()
            application_processing_duration_seconds.labels(**labels).observe(elapsed)

        return Response({"status": "ok"}, status=status.HTTP_200_OK)
