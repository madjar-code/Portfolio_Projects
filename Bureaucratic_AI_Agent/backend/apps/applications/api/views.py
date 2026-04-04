from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.applications.models import Application
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
