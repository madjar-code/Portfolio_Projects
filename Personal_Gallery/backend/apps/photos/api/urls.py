from django.urls import path
from .views import (
    CurrentUserEntries,
    EntryDetailView,
    EntryCreateView,
    EntryUpdateView,
    EntryDeleteView,
    PhotoListView,
    PhotoCreateView,
    PhotoDetailView,
    PhotoUpdateView,
    PhotoDeleteView,
)

app_name = "photos"

urlpatterns = [
    # Entry endpoints
    path("entries/", CurrentUserEntries.as_view(), name="current-user-entries"),
    path("entries/create/", EntryCreateView.as_view(), name="entry-create"),
    path("entries/<slug:entry_slug>/", EntryDetailView.as_view(), name="entry-detail"),
    path("entries/<slug:entry_slug>/update/", EntryUpdateView.as_view(), name="entry-update"),
    path("entries/<slug:entry_slug>/delete/", EntryDeleteView.as_view(), name="entry-delete"),

    # Photo endpoints
    path("photos/", PhotoListView.as_view(), name="photo-list"),
    path("photos/create/", PhotoCreateView.as_view(), name="photo-create"),
    path("photos/<uuid:photo_id>/", PhotoDetailView.as_view(), name="photo-detail"),
    path("photos/<uuid:photo_id>/update/", PhotoUpdateView.as_view(), name="photo-update"),
    path("photos/<uuid:photo_id>/delete/", PhotoDeleteView.as_view(), name="photo-delete"),
]