"""config/settings/dev.py — Development & test overrides."""
import os

from .base import *   # noqa: F401, F403

DEBUG         = True
ALLOWED_HOSTS = ["*"]

if DATABASES["default"]["HOST"] == "db" and not os.path.exists("/.dockerenv"):
    DATABASES["default"]["HOST"] = "127.0.0.1"

if DATABASES["default"]["HOST"] == "db" and not os.path.exists("/.dockerenv"):
    DATABASES["default"]["HOST"] = "127.0.0.1"

# Faster password hashing — bcrypt is intentionally slow for security,
# but that makes every test that creates a user take ~300ms. MD5 is instant.
# Never use this in production.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Print emails to the console instead of sending them
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Keep production-like throttling by default so security hardening is exercised
# in development too. You can still disable it explicitly for tests when needed.
if os.getenv("DISABLE_API_THROTTLING", "").lower() in {"1", "true", "yes", "on"}:
    REST_FRAMEWORK = {
        **REST_FRAMEWORK,
        "DEFAULT_THROTTLE_CLASSES": [],
    }

REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_RATES": {
        **REST_FRAMEWORK.get("DEFAULT_THROTTLE_RATES", {}),
        "login": "10/minute",
        "auth": "30/minute",
        "billing": "120/minute",
    },
}

# Use in-memory cache in dev — requires no running Redis for local development.
# If you want to test Redis cache behaviour locally, comment this block out.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Close DB connections between tests. CONN_MAX_AGE=60 (from base) would keep
# connections alive across tests and cause "connection already closed" errors
# in the test runner when the test database is torn down between test cases.
DATABASES["default"]["CONN_MAX_AGE"] = 0

# Default to PostgreSQL in development so local/Docker environments match.
# Set USE_SQLITE_DEV=True only when you explicitly want SQLite.
if os.getenv("USE_SQLITE_DEV", "").lower() in {"1", "true", "yes", "on"}:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }

# Celery: run tasks inline in the calling thread — no worker or broker needed.
# .delay() and .apply_async() block immediately and execute synchronously.
#
# IMPORTANT: if a test uses @pytest.mark.django_db (the default, which wraps
# everything in a single transaction) AND the task calls select_for_update(),
# the task tries to acquire a row lock inside a transaction that the test also
# holds — deadlock. Use @pytest.mark.django_db(transaction=True) for any test
# that exercises billing tasks or code that uses select_for_update() in tasks.
CELERY_TASK_ALWAYS_EAGER     = True
CELERY_TASK_EAGER_PROPAGATES = True
