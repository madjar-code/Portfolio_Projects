from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.photos.models import Entry, Photo
from .serializers import (
    EntryListSerializer,
    EntryDetailSerializer,
    EntryCreateSerializer,
    EntryUpdateSerializer,
    PhotoSerializer,
    PhotoDetailSerializer,
    PhotoUpdateSerializer,
)
from .permissions import IsOwner


class CurrentUserEntries(ListAPIView):
    """List all entries for the current user."""
    serializer_class = EntryListSerializer
    permission_classes = (IsOwner,)
    queryset = Entry.active_objects.all()

    def get_queryset(self):
        return Entry.active_objects.filter(user=self.request.user)


class EntryDetailView(RetrieveAPIView):
    """Retrieve a single entry by slug with all photos."""
    serializer_class = EntryDetailSerializer
    permission_classes = (IsOwner,)
    lookup_field = "slug"
    lookup_url_kwarg = "entry_slug"

    def get_queryset(self):
        return Entry.active_objects.prefetch_related("photos")


class EntryCreateView(CreateAPIView):
    """Create a new entry without photos."""
    serializer_class = EntryCreateSerializer
    permission_classes = (IsAuthenticated,)


class EntryUpdateView(UpdateAPIView):
    """Update entry title and description."""
    serializer_class = EntryUpdateSerializer
    permission_classes = (IsOwner,)
    lookup_field = "slug"
    lookup_url_kwarg = "entry_slug"

    def get_queryset(self):
        return Entry.active_objects.filter(user=self.request.user)


class EntryDeleteView(DestroyAPIView):
    """Soft delete an entry and all its photos."""
    permission_classes = (IsOwner,)
    lookup_field = "slug"
    lookup_url_kwarg = "entry_slug"

    def get_queryset(self):
        return Entry.active_objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        """Soft delete entry and all related photos."""
        instance.soft_delete()
        instance.photos.update(is_active=False)


class PhotoCreateView(CreateAPIView):
    """Create a new photo associated with an entry by ID."""
    serializer_class = PhotoSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        """Save photo with current user as owner."""
        serializer.save(user=self.request.user)


class PhotoListView(ListAPIView):
    """List all photos for the current user."""
    serializer_class = PhotoDetailSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        return Photo.active_objects.filter(user=self.request.user).select_related("entry")


class PhotoDetailView(RetrieveAPIView):
    """Retrieve a single photo by ID."""
    serializer_class = PhotoDetailSerializer
    permission_classes = (IsOwner,)
    lookup_field = "id"
    lookup_url_kwarg = "photo_id"

    def get_queryset(self):
        return Photo.active_objects.filter(user=self.request.user).select_related("entry")


class PhotoUpdateView(UpdateAPIView):
    """Update photo (change entry)."""
    serializer_class = PhotoUpdateSerializer
    permission_classes = (IsOwner,)
    lookup_field = "id"
    lookup_url_kwarg = "photo_id"

    def get_queryset(self):
        return Photo.active_objects.filter(user=self.request.user)


class PhotoDeleteView(DestroyAPIView):
    """Soft delete a photo."""
    serializer_class = PhotoSerializer
    permission_classes = (IsOwner,)
    lookup_field = "id"
    lookup_url_kwarg = "photo_id"
    queryset = Photo.active_objects.all()

    def perform_destroy(self, instance):
        """Soft delete the photo instead of hard delete."""
        instance.soft_delete()


class PhotoValidateView(APIView):
    """Validate photo file without creating it."""
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response(
                {'error': {'message': 'Photo file is required'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use PhotoSerializer validation logic
        serializer = PhotoSerializer()

        try:
            # Validate file
            serializer.validate_file(file)

            return Response(
                {'valid': True, 'message': 'Photo is valid'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'valid': False, 'error': {'message': str(e)}},
                status=status.HTTP_400_BAD_REQUEST
            )
