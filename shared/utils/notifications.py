"""Cross-module notification helpers with delivery tracking and retries."""

from __future__ import annotations

from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from shared.models import NotificationLog


def emit_event(group: str, event_name: str, payload: dict, *, max_retries: int = 3) -> NotificationLog:
    reference_id = str(
        payload.get("result_id")
        or payload.get("report_id")
        or payload.get("invoice_id")
        or payload.get("payment_id")
        or payload.get("critical_value_id")
        or payload.get("claim_id")
        or ""
    )
    log = NotificationLog.objects.create(
        event_name=event_name,
        delivery_group=group,
        reference_id=reference_id,
        payload=payload,
        status="pending",
        max_retries=max_retries,
    )

    channel_layer = get_channel_layer()
    if not channel_layer:
        log.status = "failed"
        log.last_error = "No channel layer configured."
        log.next_retry_at = timezone.now() + timedelta(minutes=5)
        log.save(update_fields=["status", "last_error", "next_retry_at", "updated_at"])
        return log

    for attempt in range(1, max_retries + 1):
        try:
            async_to_sync(channel_layer.group_send)(
                group,
                {
                    "type": event_name,
                    "payload": payload,
                },
            )
            log.status = "delivered"
            log.retry_count = attempt - 1
            log.delivered_at = timezone.now()
            log.last_error = ""
            log.next_retry_at = None
            log.save(
                update_fields=[
                    "status",
                    "retry_count",
                    "delivered_at",
                    "last_error",
                    "next_retry_at",
                    "updated_at",
                ]
            )
            return log
        except Exception as exc:
            log.retry_count = attempt
            log.last_error = str(exc)
            log.status = "retrying" if attempt < max_retries else "failed"
            log.next_retry_at = timezone.now() + timedelta(minutes=min(attempt * 5, 30))
            log.save(update_fields=["retry_count", "last_error", "status", "next_retry_at", "updated_at"])
    return log
