from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import serializers, status

from apps.applications.models import Application, AIReport
from apps.applications.constants import ApplicationStatus

from config.redis_client import publish_sse_event
from config.hmac_auth import verify_hmac_signature


class AIReportCallbackSerializer(serializers.Serializer):
    application_id = serializers.UUIDField()
    decision = serializers.ChoiceField(choices=["ACCEPT", "REJECT"])
    validation_result = serializers.JSONField()
    extracted_data = serializers.JSONField()
    issues_found = serializers.JSONField()
    recommendations = serializers.CharField(allow_blank=True)
    processing_time_seconds = serializers.IntegerField(min_value=0)
    ai_model_used = serializers.CharField()


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

        new_status = (
            ApplicationStatus.APPROVED
            if data["decision"] == "ACCEPT"
            else ApplicationStatus.REJECTED
        )

        with transaction.atomic():
            AIReport.objects.update_or_create(
                application=application,
                defaults={
                    "validation_result": data["validation_result"],
                    "extracted_data": data["extracted_data"],
                    "issues_found": data["issues_found"],
                    "recommendations": data["recommendations"],
                    "processing_time_seconds": data["processing_time_seconds"],
                    "ai_model_used": data["ai_model_used"],
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

        return Response({"status": "ok"}, status=status.HTTP_200_OK)
