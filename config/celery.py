"""config/celery.py — Celery application factory.

Import in config/__init__.py so tasks are auto-discovered on Django startup:
    from .celery import app as celery_app
    __all__ = ("celery_app",)

Start workers:
    celery -A config worker -l info -Q default,notifications,cdss
Start beat scheduler:
    celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
"""
import os
import logging

logger = logging.getLogger(__name__)

try:
    from celery import Celery
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    logger.warning("Celery not available - async tasks disabled")

# Default to dev. In production, DJANGO_SETTINGS_MODULE is set in the
# container environment by docker-compose.yml.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

if CELERY_AVAILABLE:
    app = Celery("vh_django")
    
    # Read all CELERY_* settings from Django settings
    app.config_from_object("django.conf:settings", namespace="CELERY")

    # Auto-discover tasks in every app listed in INSTALLED_APPS
    app.autodiscover_tasks()

    # ── Queue routing ─────────────────────────────────────────────────────────────
    # Celery routes by TASK NAME (the name= argument in @shared_task).
    # All our notification tasks declare names like: name="notifications.notify_pharmacists"
    # The CDSS alert task declares: name="notifications.notify_cdss_alert"
    #   but is already assigned queue="cdss" in the decorator — the route below
    #   makes it explicit and consistent with the worker -Q flag.
    #
    # IMPORTANT: specific rules must come BEFORE wildcards. Celery checks routes
    # in dict insertion order (Python 3.7+ dicts are ordered). If the wildcard
    # "notifications.*" came first it would match notify_cdss_alert and send it
    # to the notifications queue before the specific rule is ever checked.
    app.conf.task_routes = {
        # Specific rule first — CDSS alerts go to isolated cdss queue
        "notifications.notify_cdss_alert": {"queue": "cdss"},
        # Wildcard second — all other notification tasks go to notifications queue
        "notifications.*":                 {"queue": "notifications"},
    }
else:
    app = None