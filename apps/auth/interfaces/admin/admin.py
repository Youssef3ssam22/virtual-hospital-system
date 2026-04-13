"""Django admin configuration for auth."""
from django.contrib import admin

from apps.auth.infrastructure.orm_models import User, AuthToken


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin for User model."""
    
    list_display = ("email", "full_name", "is_active", "last_login", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("email", "full_name")
    readonly_fields = ("id", "created_at", "updated_at")
    
    fieldsets = (
        ("Identity", {"fields": ("id", "email", "full_name")}),
        ("Security", {"fields": ("password_hash", "is_active")}),
        ("Timestamps", {"fields": ("last_login", "created_at", "updated_at")}),
    )


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    """Admin for AuthToken model."""
    
    list_display = ("user", "token_type", "is_valid", "expires_at", "created_at")
    list_filter = ("is_valid", "token_type", "created_at")
    search_fields = ("user__email", "access_token")
    readonly_fields = ("id", "access_token", "refresh_token", "created_at")
    
    fieldsets = (
        ("User", {"fields": ("user",)}),
        ("Tokens", {"fields": ("access_token", "refresh_token", "token_type")}),
        ("Status", {"fields": ("is_valid", "expires_at")}),
        ("Timestamps", {"fields": ("created_at",)}),
    )
