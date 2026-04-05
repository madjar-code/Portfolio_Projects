from django.conf import settings
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import serializers, status

from apps.applications.models import Application, AIReport
from apps.applications.constants import ApplicationStatus


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
    Authenticated by X-API-Key header (not JWT — agent has no user account).
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        api_key = request.headers.get("X-API-Key", "")
        if not settings.AGENT_API_KEY or api_key != settings.AGENT_API_KEY:
            return Response(
                {"error": {"message": "Invalid or missing API key."}},
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
            application = Application.objects.get(id=data["application_id"])
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

        return Response({"status": "ok"}, status=status.HTTP_200_OK)
