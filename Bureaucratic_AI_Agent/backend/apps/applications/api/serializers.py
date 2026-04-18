import json
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from apps.applications.constants import PROCEDURES
from apps.applications.models import Application, Document, AIReport
from apps.applications.metrics import applications_created_total


class AIReportSerializer(ModelSerializer):
    class Meta:
        model = AIReport
        fields = (
            "decision",
            "confidence_score",
            "extracted_data",
            "issues_found",
            "recommendations",
            "ai_model_used",
            "prompt_version",
            "processing_time_seconds",
            "created_at",
        )


class DocumentSerializer(ModelSerializer):
    class Meta:
        model = Document
        fields = (
            "id",
            "file_name",
            "file_format",
            "file",
            "created_at",
        )


class ApplicationListSerializer(ModelSerializer):
    class Meta:
        model = Application
        fields = (
            "id",
            "application_number",
            "procedure",
            "status",
            "created_at",
        )


class ApplicationCreateSerializer(ModelSerializer):
    document = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Application
        fields = (
            "procedure",
            "form_data",
            "document",
        )

    def validate_form_data(self, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON.")
        return value

    def validate(self, attrs):
        procedure = attrs.get("procedure")
        meta = PROCEDURES.get(procedure, {})
        if meta.get("document_required", True) and not attrs.get("document"):
            raise serializers.ValidationError({"document": "This procedure requires a document."})
        return attrs

    def create(self, validated_data):
        document_file = validated_data.pop("document", None)
        user = self.context["request"].user
        application = Application.objects.create(user=user, **validated_data)
        if document_file is not None:
            Document.objects.create(
                application=application,
                user=user,
                file=document_file,
            )
        applications_created_total.labels(procedure=application.procedure).inc()
        return application

    def to_representation(self, instance):
        return ApplicationDetailSerializer(instance, context=self.context).data


class ApplicationDetailSerializer(ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    report = AIReportSerializer(read_only=True)

    class Meta:
        model = Application
        fields = (
            "id",
            "application_number",
            "procedure",
            "status",
            "form_data",
            "submitted_at",
            "created_at",
            "updated_at",
            "documents",
            "report",
        )