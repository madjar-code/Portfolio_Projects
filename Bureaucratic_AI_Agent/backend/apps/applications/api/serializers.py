import json
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from apps.applications.models import Application, Document, AIReport


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
    document = serializers.FileField(write_only=True)

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

    def create(self, validated_data):
        document_file = validated_data.pop("document")
        user = self.context["request"].user
        application = Application.objects.create(user=user, **validated_data)
        Document.objects.create(
            application=application,
            user=user,
            file=document_file,
        )
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