from django.db.models import Manager
from django.db.models import QuerySet


class SoftDeletionManager(Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(is_active=True)
