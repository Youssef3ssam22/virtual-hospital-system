"""Django admin registrations for shared infrastructure records."""

from django.contrib import admin

from shared.models import IdempotencyRecord, NotificationLog


@admin.register(IdempotencyRecord)
class IdempotencyRecordAdmin(admin.ModelAdmin):
    list_display = ("key", "actor_id", "method", "path", "status", "response_code", "processed_at")
    list_filter = ("status", "method", "created_at")
    search_fields = ("key", "actor_id", "path")
    ordering = ("-created_at",)
    readonly_fields = (
        "id",
        "actor_id",
        "key",
        "method",
        "path",
        "request_hash",
        "status",
        "response_code",
        "response_body",
        "processed_at",
        "created_at",
        "updated_at",
    )


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("event_name", "delivery_group", "reference_id", "status", "retry_count", "delivered_at")
    list_filter = ("status", "event_name", "delivery_group", "created_at")
    search_fields = ("event_name", "reference_id", "delivery_group")
    ordering = ("-created_at",)
    readonly_fields = (
        "id",
        "event_name",
        "delivery_group",
        "reference_id",
        "payload",
        "status",
        "retry_count",
        "max_retries",
        "last_error",
        "delivered_at",
        "next_retry_at",
        "created_at",
        "updated_at",
    )
