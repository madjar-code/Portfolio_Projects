from django.urls import path
from .views import (
    ProcedureListView,
    CurrentUserApplications,
    ApplicationDetailView,
    ApplicationCreateView,
    ApplicationSubmitView,
)
from .callback import CallbackView

urlpatterns = [
    path("procedures/", ProcedureListView.as_view(), name="procedure-list"),
    path("applications/", CurrentUserApplications.as_view(), name="application-list"),
    path("applications/create/", ApplicationCreateView.as_view(), name="application-create"),
    path("applications/<str:application_number>/", ApplicationDetailView.as_view(), name="application-detail"),
    path("applications/<str:application_number>/submit/", ApplicationSubmitView.as_view(), name="application-submit"),
    path("callback/", CallbackView.as_view(), name="agent-callback"),
]
