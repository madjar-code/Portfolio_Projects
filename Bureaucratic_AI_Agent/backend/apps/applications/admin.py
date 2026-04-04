from django.contrib import admin

from .models import AIReport, Application, Document


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0
    fields = ("file", "file_name", "file_format", "file_size", "is_active")
    readonly_fields = ("file_name", "file_format", "file_size")


class AIReportInline(admin.StackedInline):
    model = AIReport
    extra = 0
    readonly_fields = (
        "validation_result",
        "extracted_data",
        "issues_found",
        "recommendations",
        "processing_time_seconds",
        "ai_model_used",
        "created_at",
        "updated_at",
    )
    can_delete = False


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("application_number", "user", "procedure", "status", "created_at")
    list_filter = ("status", "procedure")
    search_fields = ("application_number",)
    readonly_fields = ("application_number", "created_at", "updated_at", "submitted_at")
    inlines = (DocumentInline, AIReportInline)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Document) and not instance.user_id:
                instance.user = request.user
            instance.save()
        formset.save_m2m()
