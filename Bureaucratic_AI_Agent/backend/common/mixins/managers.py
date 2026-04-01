from django.db.models import Manager, QuerySet


class SoftDeletionQuerySet(QuerySet):
    def delete(self):
        return self.update(is_active=False)

    def restore(self):
        return self.update(is_active=True)


class SoftDeletionManager(Manager):
    def get_queryset(self) -> SoftDeletionQuerySet:
        return SoftDeletionQuerySet(self.model, using=self._db).filter(is_active=True)
