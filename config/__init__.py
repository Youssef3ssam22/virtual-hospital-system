# Expose Celery app so Django finds it during startup.
# This is required for @shared_task decorators to work correctly.
from .celery import app as celery_app  # noqa: F401

__all__ = ("celery_app",)
