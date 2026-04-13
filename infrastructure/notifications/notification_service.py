"""infrastructure/notifications/notification_service.py — In-app notification storage."""
import logging
from django.db import models
from django.utils import timezone
from shared.domain.ports import NotificationPort

log = logging.getLogger("virtual_hospital.notifications")


class Notification(models.Model):
    """In-app notification stored in the database.

    Staff members read their notifications via GET /api/v1/notifications/.
    Notifications are created by Celery tasks triggered by domain events,
    so the HTTP request thread is never blocked by notification writes.
    """
    recipient = models.ForeignKey(
        "authentication.Staff", on_delete=models.CASCADE,
        related_name="notifications", db_column="recipient_id",
    )
    title             = models.CharField(max_length=255)
    message           = models.TextField()
    notification_type = models.CharField(max_length=50)
    entity_type       = models.CharField(max_length=100, null=True, blank=True)
    entity_id         = models.CharField(max_length=50,  null=True, blank=True)
    is_read           = models.BooleanField(default=False, db_index=True)
    created_at        = models.DateTimeField(db_index=True)

    class Meta:
        app_label = "authentication"
        db_table  = "notifications"
        ordering  = ["-created_at"]
        indexes   = [
            models.Index(fields=["recipient", "is_read"], name="ix_notif_recip_read"),
        ]

    def __str__(self):
        return f"[{self.notification_type}] {self.title} → {self.recipient_id}"


class NotificationService(NotificationPort):
    """Persists notifications to the database.

    send()         — one notification to one specific staff member by ID
    send_to_role() — one notification to every active staff member with the given role
    """

    def send(self, recipient_id: str, title: str, message: str,
             notification_type: str, entity_type: str = None,
             entity_id: str = None) -> None:
        Notification.objects.create(
            recipient_id=recipient_id,
            title=title,
            message=message,
            notification_type=notification_type,
            entity_type=entity_type,
            entity_id=entity_id,
            is_read=False,
            created_at=timezone.now(),
        )

    def send_to_role(self, role: str, title: str, message: str,
                     notification_type: str, entity_type: str = None,
                     entity_id: str = None) -> None:
        from apps.authentication.infrastructure.orm_models import Staff

        staff_list = list(Staff.objects.filter(role=role, is_active=True).values_list("id", flat=True))
        if not staff_list:
            log.debug("[NOTIFY] No active staff with role=%s to notify", role)
            return

        now = timezone.now()
        Notification.objects.bulk_create([
            Notification(
                recipient_id=str(staff_id),
                title=title,
                message=message,
                notification_type=notification_type,
                entity_type=entity_type,
                entity_id=entity_id,
                is_read=False,
                created_at=now,
            )
            for staff_id in staff_list
        ])
        log.debug("[NOTIFY] %s → role=%s (%d recipients): %s",
                  notification_type, role, len(staff_list), title)