from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

from config.yasg import info

schema_view = get_schema_view(
    info,
    public=True,
    permission_classes=(AllowAny,)
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.auth.api.urls")),
    path("api/v1/", include("apps.applications.api.urls")),
]

if settings.DEBUG:
    # API Documentation
    urlpatterns += [
        re_path(
            r"^swagger(?P<format>\.json|\.yaml)$",
            schema_view.without_ui(cache_timeout=0),
            name="schema-json",
        ),
        path(
            "swagger/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path(
            "redoc/",
            schema_view.with_ui("redoc", cache_timeout=0),
            name="schema-redoc",
        ),
        path(
            "",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-root",
        ),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
