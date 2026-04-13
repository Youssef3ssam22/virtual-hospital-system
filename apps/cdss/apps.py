"""CDSS module configuration."""

from django.apps import AppConfig


class CDSSConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cdss"
    verbose_name = "Clinical Decision Support System"
