import logging

from django.utils import timezone
from kombu.exceptions import OperationalError as KombuOperationalError
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.applications.models import Application, ApplicationStatus
from apps.applications.metrics import applications_submitted_total
from apps.applications.constants import PROCEDURES
from .serializers import (
    ApplicationListSerializer,
    ApplicationDetailSerializer,
    ApplicationCreateSerializer,
    ApplicationUpdateSerializer,
)
from .permissions import IsOwner

logger = logging.getLogger(__name__)


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


NON_DELETABLE_STATUSES = {ApplicationStatus.SUBMITTED, ApplicationStatus.PROCESSING}


class ApplicationDetailView(APIView):
    """GET/PATCH/DELETE a single application by application_number."""
    permission_classes = (IsOwner,)
    parser_classes = (MultiPartParser, FormParser)

    def _get_application(self, request, application_number):
        return Application.active_objects.filter(
            application_number=application_number,
            user=request.user,
        ).prefetch_related("documents").select_related("report").first()

    def get(self, request, application_number):
        app = self._get_application(request, application_number)
        if app is None:
            return Response({"error": {"message": "Application not found."}}, status=status.HTTP_404_NOT_FOUND)
        return Response(ApplicationDetailSerializer(app, context={"request": request}).data)

    def patch(self, request, application_number):
        app = self._get_application(request, application_number)
        if app is None:
            return Response({"error": {"message": "Application not found."}}, status=status.HTTP_404_NOT_FOUND)
        if app.status != ApplicationStatus.DRAFT:
            return Response(
                {"error": {"message": "Only DRAFT applications can be edited."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ApplicationUpdateSerializer(app, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, application_number):
        app = self._get_application(request, application_number)
        if app is None:
            return Response({"error": {"message": "Application not found."}}, status=status.HTTP_404_NOT_FOUND)
        if app.status in NON_DELETABLE_STATUSES:
            return Response(
                {"error": {"message": "Applications in SUBMITTED or PROCESSING state cannot be deleted."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        app.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        try:
            process_application.delay(str(application.id))
        except (KombuOperationalError, ConnectionError) as exc:
            logger.error(
                "reliability=enqueue_failed application=%s error=%s",
                application.id, exc,
            )
            application.status = ApplicationStatus.FAILED
            application.save(update_fields=["status", "updated_at"])
            return Response(
                {"error": {"message": "Task queue unavailable. Please try again later."}},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        serializer = ApplicationDetailSerializer(application, context={"request": request})
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
