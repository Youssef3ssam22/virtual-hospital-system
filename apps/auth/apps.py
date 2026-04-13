"""Authentication app configuration."""

from django.apps import AppConfig


class AuthConfig(AppConfig):
    """Configuration for the authentication module."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.auth"
    label = "hospital_auth"
    verbose_name = "Hospital Authentication"
    
    def ready(self):
        """Import admin when Django is ready."""
        from apps.auth.interfaces.admin import admin as auth_admin  # noqa: F401
