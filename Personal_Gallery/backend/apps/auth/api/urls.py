from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from .views import GoogleOAuthView, GoogleOAuthCodeView

app_name = "auth"

urlpatterns = [
    # Djoser endpoints (registration, activation, password reset, etc.)
    path("", include("djoser.urls")),

    # JWT endpoints
    path("", include("djoser.urls.jwt")),

    # Google OAuth endpoints
    path("google/token/", GoogleOAuthView.as_view(), name="google-oauth"),
    path("google/code/", GoogleOAuthCodeView.as_view(), name="google-oauth-code"),
]
