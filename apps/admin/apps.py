"""Admin module configuration."""

from django.apps import AppConfig


class AdminConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.admin"
    label = "hospital_administration"
    verbose_name = "Administration"
