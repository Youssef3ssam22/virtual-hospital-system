"""Shared infrastructure models used across modules."""

from __future__ import annotations

import uuid

from django.db import models
from django.utils import timezone


class IdempotencyRecord(models.Model):
    """Stores deduplicated POST requests for critical write endpoints."""

    STATUS_CHOICES = [
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor_id = models.CharField(max_length=255, blank=True, default="anonymous")
    key = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=500)
    request_hash = models.CharField(max_length=128)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="processing")
    response_code = models.PositiveIntegerField(null=True, blank=True)
    response_body = models.JSONField(default=dict, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shared_idempotency_records"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["actor_id", "key", "method", "path"],
                name="uq_idempotency_actor_key_method_path",
            )
        ]
        indexes = [
            models.Index(fields=["path", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def mark_completed(self, response_code: int, response_body: dict | list | str | None) -> None:
        self.status = "completed"
        self.response_code = response_code
        self.response_body = response_body or {}
        self.processed_at = timezone.now()

    def mark_failed(self, response_code: int, response_body: dict | list | str | None) -> None:
        self.status = "failed"
        self.response_code = response_code
        self.response_body = response_body or {}
        self.processed_at = timezone.now()


class NotificationLog(models.Model):
    """Persistent delivery log for notifications and websocket events."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("delivered", "Delivered"),
        ("retrying", "Retrying"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_name = models.CharField(max_length=150, db_index=True)
    delivery_group = models.CharField(max_length=150, db_index=True)
    reference_id = models.CharField(max_length=255, blank=True, default="")
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    last_error = models.TextField(blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shared_notification_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "next_retry_at"]),
            models.Index(fields=["event_name", "created_at"]),
        ]

