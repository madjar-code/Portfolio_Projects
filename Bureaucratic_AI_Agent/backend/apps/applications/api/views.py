from django.utils import timezone
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.applications.models import Application, ApplicationStatus
from apps.applications.metrics import applications_submitted_total
from apps.applications.constants import PROCEDURES
from .serializers import ApplicationListSerializer, ApplicationDetailSerializer, ApplicationCreateSerializer
from .permissions import IsOwner


class ProcedureListView(APIView):
    """List all available procedures with their metadata."""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        procedures = [
            {"code": code, **meta}
            for code, meta in PROCEDURES.items()
        ]
        return Response(procedures, status=status.HTTP_200_OK)


class CurrentUserApplications(ListAPIView):
    """List all applications for the current user."""
    serializer_class = ApplicationListSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        return Application.active_objects.filter(user=self.request.user)


class ApplicationDetailView(RetrieveAPIView):
    """Retrieve a single application by application_number with documents and report."""
    serializer_class = ApplicationDetailSerializer
    permission_classes = (IsOwner,)
    lookup_field = "application_number"
    lookup_url_kwarg = "application_number"

    def get_queryset(self):
        return Application.active_objects.filter(
            user=self.request.user
        ).prefetch_related("documents").select_related("report")


class ApplicationCreateView(CreateAPIView):
    """Create a new application with a single document."""
    serializer_class = ApplicationCreateSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)


class ApplicationSubmitView(APIView):
    """Submit a DRAFT application for AI processing. Returns 202 Accepted."""
    permission_classes = (IsOwner,)

    def post(self, request, application_number):
        application = Application.active_objects.filter(
            application_number=application_number,
            user=request.user,
        ).first()

        if application is None:
            return Response(
                {"error": {"message": "Application not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        if application.status != ApplicationStatus.DRAFT:
            return Response(
                {"error": {"message": f"Only DRAFT applications can be submitted. Current status: {application.status}."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.status = ApplicationStatus.SUBMITTED
        application.submitted_at = timezone.now()
        application.save(update_fields=["status", "submitted_at", "updated_at"])

        applications_submitted_total.labels(procedure=application.procedure).inc()

        from apps.applications.tasks.process_application import process_application
        process_application.delay(str(application.id))

        serializer = ApplicationDetailSerializer(application, context={"request": request})
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
