"""infrastructure/database/base_repository.py — Base repository with common helpers."""
from django.db import models


class BaseRepository:
    """Base class for all Django ORM repositories.

    Subclasses must set model_class to a Django Model class.
    A missing model_class is caught at first method call with a clear error.
    """

    model_class: type[models.Model] = None

    def _check_model_class(self) -> None:
        # FIX: was silently crashing with a confusing TypeError when model_class
        # was not set. Now raises a clear error pointing at the subclass.
        if self.model_class is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must set model_class before calling repository methods."
            )

    def get_by_id(self, pk: str):
        self._check_model_class()
        try:
            return self.model_class.objects.get(pk=pk)
        except self.model_class.DoesNotExist:
            return None

    def save(self, instance: models.Model) -> models.Model:
        instance.save()
        return instance

    def delete(self, pk: str) -> None:
        self._check_model_class()
        self.model_class.objects.filter(pk=pk).delete()