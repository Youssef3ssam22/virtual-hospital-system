"""
config/settings/base.py
Shared settings for all environments.
"""
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")

VERSION = "2.0.0"

INSTALLED_APPS = [
    # Authentication MUST come first — AUTH_USER_MODEL must be registered
    # before django.contrib.admin loads its own models
    "apps.auth.apps.AuthConfig",
    # Django built-ins
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "channels",
    "shared",
    # Hospital domain apps
    "apps.patients.apps.PatientsConfig",
    "apps.admin.apps.AdminConfig",
    "apps.lab.apps.LabConfig",
    "apps.radiology.apps.RadiologyConfig",
    "apps.pharmacy.apps.PharmacyConfig",
    "apps.billing.apps.BillingConfig",
    "apps.cdss.apps.CDSSConfig",
    # NOTE: apps.fhir and apps.files are NOT listed here because they do not
    # exist in the project yet. Add them once their app folders are created.
    # "apps.fhir",
    # "apps.files",
    # Celery result/beat storage
    "django_celery_beat",
    "django_celery_results",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",        # must be first — sets CORS headers before any response
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "shared.utils.idempotency.IdempotencyMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "infrastructure.audit.audit_logger.AuditMiddleware",  # last — wraps full request cycle
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION  = "config.asgi.application"

# ── Database ──────────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends.postgresql",
        "NAME":     config("DB_NAME",     default="virtual_hospital"),
        "USER":     config("DB_USER",     default="postgres"),
        # Empty default forces explicit configuration — no hardcoded passwords in source
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST":     config("DB_HOST",     default="localhost"),
        "PORT":     config("DB_PORT",     default="5432"),
        "OPTIONS":  {"options": "-c timezone=UTC"},
        # Without CONN_MAX_AGE every request opens and closes a DB connection.
        # 60 seconds keeps connections alive across requests in the same worker process.
        # dev.py overrides this to 0 so test transactions don't leak between tests.
        "CONN_MAX_AGE": config("DB_CONN_MAX_AGE", default=60, cast=int),
    }
}

AUTH_USER_MODEL = "hospital_auth.User"

# ── Password validation ───────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    # UserAttributeSimilarityValidator is intentionally excluded.
    # It compares the password against USERNAME_FIELD which is now employee_number
    # (e.g. "EMP001234"). It would block passwords containing "emp" or digits
    # that appear in the employee number — unhelpful and confusing for clinical staff.
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── Internationalisation ──────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE     = "UTC"
USE_I18N      = True
USE_TZ        = True

# ── Static & Media ────────────────────────────────────────────────────────────
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL   = "/media/"
MEDIA_ROOT  = BASE_DIR / config("MEDIA_ROOT", default="uploads")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Session ───────────────────────────────────────────────────────────────────
# Custom cookie name prevents clashes if another Django app runs on the same domain.
SESSION_COOKIE_NAME = "vh_session"
# Session expires when the browser is closed — critical for a hospital system
# where staff share terminals. A nurse who forgets to log out should not leave
# an active session behind when the browser is closed.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# Hard upper limit — even if the browser stays open, force re-login after 8 hours
# (one full hospital shift). Prevents indefinitely open sessions on ward terminals.
SESSION_COOKIE_AGE = 28800  # 8 hours in seconds

# ── Django REST Framework ─────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.auth.infrastructure.authentication.BearerTokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "shared.utils.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS":  "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER":     "shared.utils.exception_handler.custom_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon":  "100/hour",
        "user":  "1000/hour",
        "login": "10/minute",
        "auth": "30/minute",
        "billing": "120/minute",
    },
}

# ── DRF Spectacular (OpenAPI / Swagger) ───────────────────────────────────────
SPECTACULAR_SETTINGS = {
    "TITLE":       "Virtual Hospital Information System",
    "DESCRIPTION": "Complete Hospital IS — patients, encounters, labs, pharmacy, radiology, nursing, billing, CDSS.",
    "VERSION":     VERSION,
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization":   True,
        "displayRequestDuration": True,
        "filter": True,
    },
}

# ── Django Admin Theme (Jazzmin) ─────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    "site_title": "Virtual Hospital Command Center",
    "site_header": "Virtual Hospital Command Center",
    "site_brand": "VH Command Center",
    "site_logo_classes": "img-circle",
    "welcome_sign": "Hospital operations, laboratory control, and billing oversight",
    "copyright": "Virtual Hospital",
    "search_model": "hospital_auth.User",
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index"},
        {"name": "API Docs", "url": "/api/docs/", "new_window": True},
        {"name": "Health", "url": "/health/", "new_window": True},
    ],
    "usermenu_links": [
        {"name": "API Docs", "url": "/api/docs/", "new_window": True},
        {"name": "Health", "url": "/health/", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "related_modal_active": True,
    "show_ui_builder": False,
    "custom_css": "admin/custom.css",
    "order_with_respect_to": [
        "apps.admin",
        "apps.patients",
        "apps.lab",
        "apps.billing",
        "apps.radiology",
        "apps.pharmacy",
        "apps.cdss",
        "hospital_auth",
    ],
    "icons": {
        "apps.admin.AdminUser": "fas fa-user-shield",
        "apps.admin.Department": "fas fa-sitemap",
        "apps.admin.Ward": "fas fa-warehouse",
        "apps.admin.Bed": "fas fa-procedures",
        "apps.admin.SystemSettings": "fas fa-sliders-h",
        "apps.admin.Role": "fas fa-user-tag",
        "apps.admin.Permission": "fas fa-key",
        "apps.admin.UserRole": "fas fa-user-cog",
        "apps.admin.AuditLog": "fas fa-clipboard-check",
        "apps.admin.LabCatalogItem": "fas fa-vials",
        "apps.admin.RadiologyCatalogItem": "fas fa-x-ray",
        "apps.admin.ServiceCatalogItem": "fas fa-stethoscope",
        "apps.patients.Patient": "fas fa-user-injured",
        "apps.patients.PatientAllergy": "fas fa-allergies",
        "apps.lab.LabOrder": "fas fa-file-medical",
        "apps.lab.Specimen": "fas fa-vial",
        "apps.lab.LabResult": "fas fa-flask",
        "apps.lab.LabReport": "fas fa-file-signature",
        "apps.lab.CriticalValue": "fas fa-exclamation-triangle",
        "apps.lab.AnalyzerQueue": "fas fa-stream",
        "apps.lab.RecollectionRequest": "fas fa-redo-alt",
        "apps.billing.PatientAccount": "fas fa-wallet",
        "apps.billing.Invoice": "fas fa-file-invoice-dollar",
        "apps.billing.InvoiceLineItem": "fas fa-receipt",
        "apps.billing.Payment": "fas fa-credit-card",
        "apps.billing.InsuranceClaim": "fas fa-file-contract",
        "apps.billing.ClaimDenial": "fas fa-ban",
        "apps.billing.FinancialTimeline": "fas fa-chart-line",
        "apps.billing.BillingStats": "fas fa-chart-pie",
        "hospital_auth.User": "fas fa-user-md",
        "auth.Group": "fas fa-users-cog",
    },
}

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "dark_mode_theme": None,
    "navbar": "navbar-dark",
    "sidebar": "sidebar-dark-primary",
    "accent": "accent-info",
    "brand_colour": "navbar-primary",
    "button_classes": {
        "primary": "btn btn-primary",
        "secondary": "btn btn-outline-secondary",
        "info": "btn btn-info",
        "warning": "btn btn-warning",
        "danger": "btn btn-danger",
        "success": "btn btn-success",
    },
}

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in config(
        "CORS_ALLOWED_ORIGINS",
        default="http://localhost:3000,http://localhost:5173",
    ).split(",")
    if o.strip()  # guard against trailing comma in .env producing an empty string
]
CORS_ALLOW_CREDENTIALS = True

# ── CDSS ──────────────────────────────────────────────────────────────────────
CDSS_MOCK_MODE = config("CDSS_MOCK_MODE", default=True, cast=bool)

# ── Neo4j ─────────────────────────────────────────────────────────────────────
NEO4J_URI      = config("NEO4J_URI",      default="bolt://localhost:7687")
NEO4J_USER     = config("NEO4J_USER",     default="neo4j")
NEO4J_PASSWORD = config("NEO4J_PASSWORD", default="password")

# ── Logging ───────────────────────────────────────────────────────────────────
# Create the logs directory if it doesn't exist. Without this, RotatingFileHandler
# raises FileNotFoundError on startup and the entire server fails to start.
_LOG_DIR = BASE_DIR / "logs"
_LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format":  "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class":     "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class":       "logging.handlers.RotatingFileHandler",
            "filename":    str(_LOG_DIR / "hospital.log"),
            "maxBytes":    10_000_000,
            "backupCount": 5,
            "formatter":   "default",
        },
    },
    "root": {"level": "INFO", "handlers": ["console", "file"]},
    "loggers": {
        "virtual_hospital":       {"level": "DEBUG", "propagate": True},
        "virtual_hospital.audit": {"level": "INFO",  "propagate": True},
        "virtual_hospital.tasks": {"level": "INFO",  "propagate": True},
        "cdss":                   {"level": "DEBUG", "propagate": True},
    },
}

# ── Channels (WebSockets) ─────────────────────────────────────────────────────
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# ── Caches ────────────────────────────────────────────────────────────────────
# Cache uses Redis DB /1. Celery broker uses DB /0 (defined below).
# Keeping them on separate DBs means flushing the cache never deletes Celery tasks.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_CACHE_URL", default="redis://localhost:6379/1"),
        "OPTIONS":  {"socket_connect_timeout": 5, "socket_timeout": 5},
        "TIMEOUT":  300,
    }
}

# ── Celery ────────────────────────────────────────────────────────────────────
# Broker on Redis DB /0 — separate from the cache on DB /1
CELERY_BROKER_URL           = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND       = "django-db"
CELERY_ACCEPT_CONTENT       = ["json"]
CELERY_TASK_SERIALIZER      = "json"
CELERY_RESULT_SERIALIZER    = "json"
CELERY_TIMEZONE             = TIME_ZONE
CELERY_TASK_TRACK_STARTED   = True
CELERY_TASK_TIME_LIMIT      = 300
CELERY_TASK_SOFT_TIME_LIMIT = 240
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
