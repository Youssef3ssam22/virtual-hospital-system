"""config/settings/prod.py — Production overrides.
All settings here assume: nginx in front, HTTPS terminated at nginx,
gunicorn running inside Docker, environment variables from .env file.
"""
from decouple import config
from .base import *   # noqa: F401, F403

DEBUG = False

# ── Allowed hosts ─────────────────────────────────────────────────────────────
# Fail fast on startup rather than silently returning 400 on every request.
_raw_hosts = config("ALLOWED_HOSTS", default=None)
if not _raw_hosts:
    raise RuntimeError(
        "ALLOWED_HOSTS is not configured. "
        "Add ALLOWED_HOSTS=yourdomain.com to your .env file before starting production."
    )
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(",") if h.strip()]

# ── Security ──────────────────────────────────────────────────────────────────
# SECURE_SSL_REDIRECT must be False when nginx terminates SSL.
# With it True: nginx sends HTTP to gunicorn → Django redirects to HTTPS →
# nginx sends HTTP again → infinite redirect loop.
# Instead, tell Django to trust the X-Forwarded-Proto header that nginx sets.
SECURE_SSL_REDIRECT      = False
SECURE_PROXY_SSL_HEADER  = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_HSTS_SECONDS            = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD            = True
SESSION_COOKIE_SECURE          = True
CSRF_COOKIE_SECURE             = True
# NOTE: SECURE_BROWSER_XSS_FILTER and SECURE_CONTENT_TYPE_NOSNIFF were removed
# from Django 5.0 — they are now always on and cannot be toggled.
# Do not add them here; Django 5 will raise SystemCheckError if you do.

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND       = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST          = config("EMAIL_HOST",          default="smtp.sendgrid.net")
EMAIL_PORT          = config("EMAIL_PORT",          default=587, cast=int)
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = config("EMAIL_HOST_USER",     default="apikey")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL  = config("DEFAULT_FROM_EMAIL",  default="noreply@hospital.com")

# ── Cache ─────────────────────────────────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_CACHE_URL", default="redis://localhost:6379/1"),
        "OPTIONS":  {"socket_connect_timeout": 5, "socket_timeout": 5},
        "TIMEOUT":  600,
    }
}

# ── Sentry error monitoring ───────────────────────────────────────────────────
_SENTRY_DSN = config("SENTRY_DSN", default="")
if _SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    sentry_sdk.init(
        dsn=_SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )

# ── Logging ───────────────────────────────────────────────────────────────────
# Production logs to stdout only — Docker captures it and forwards to whatever
# log aggregator is configured (CloudWatch, Loki, Datadog, etc.).
# Use JSON format if pythonjsonlogger is installed, plain text as fallback.
def _build_formatter() -> dict:
    try:
        import pythonjsonlogger.jsonlogger  # noqa: F401
        return {
            "()":     "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        }
    except ImportError:
        return {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "prod": _build_formatter(),
    },
    "handlers": {
        "console": {
            "class":     "logging.StreamHandler",
            "formatter": "prod",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "virtual_hospital":       {"level": "INFO",  "propagate": True},
        "virtual_hospital.audit": {"level": "INFO",  "propagate": True},
        "django.security":        {"level": "ERROR", "propagate": True},
        "django.request":         {"level": "ERROR", "propagate": True},
    },
}