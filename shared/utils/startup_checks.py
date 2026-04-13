"""shared/utils/startup_checks.py — Validates required environment variables at startup.

HOW TO USE — call this from a Django AppConfig.ready() method.
The best place is a dedicated config app. Create config/apps.py:

    from django.apps import AppConfig

    class ConfigApp(AppConfig):
        name = "config"

        def ready(self):
            from shared.utils.startup_checks import run_startup_checks
            run_startup_checks()

Then add "config" to INSTALLED_APPS in base.py.

Why: Django starts silently even with missing required environment variables.
Without this check, you deploy to production, the server starts, and the first
request fails with a cryptic error deep in the stack. run_startup_checks() raises
ImproperlyConfigured immediately on startup so the failure is obvious and fast.
"""
import os
import logging
from django.core.exceptions import ImproperlyConfigured

log = logging.getLogger("virtual_hospital")

# Variables that MUST be set in production — missing any of these will
# break the server in a non-obvious way.
REQUIRED_IN_PRODUCTION = [
    "SECRET_KEY",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_HOST",
    "REDIS_URL",
    # FIX: REDIS_CACHE_URL was missing — it's a separate setting from REDIS_URL.
    # If only REDIS_URL is set, the cache falls back silently to a broken state.
    "REDIS_CACHE_URL",
    "ALLOWED_HOSTS",
]

# Variables that improve functionality but have workable defaults.
RECOMMENDED = [
    "EMAIL_HOST_PASSWORD",   # email sending won't work without this
    "SENTRY_DSN",            # error monitoring disabled without this
    "CORS_ALLOWED_ORIGINS",  # browser clients may be blocked without this
    "STAFF_DEFAULT_PASSWORD", # seed data uses a weak default without this
]


def run_startup_checks() -> None:
    """Check required environment variables.

    In production (DEBUG=False): raises ImproperlyConfigured on any missing
    required variable — the server will not start.

    In development (DEBUG=True): logs warnings for recommended variables,
    never blocks startup.
    """
    from django.conf import settings

    if settings.DEBUG:
        for var in RECOMMENDED:
            if not os.environ.get(var):
                log.debug("Optional env var not set: %s", var)
        return

    # Production: fail fast
    missing = [v for v in REQUIRED_IN_PRODUCTION if not os.environ.get(v)]
    if missing:
        raise ImproperlyConfigured(
            f"The following required environment variables are not set: "
            f"{', '.join(missing)}. "
            f"Check your .env file or deployment environment configuration."
        )

    for var in RECOMMENDED:
        if not os.environ.get(var):
            log.warning("Recommended env var is not set: %s", var)