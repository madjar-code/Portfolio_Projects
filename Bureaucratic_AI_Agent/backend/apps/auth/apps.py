from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    name = "apps.auth"
    label = "auth_app"
    default_auto_field = "django.db.models.BigAutoField"