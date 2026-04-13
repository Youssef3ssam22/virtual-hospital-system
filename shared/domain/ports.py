"""shared/domain/ports.py — Abstract ports for infrastructure services.

Use cases depend ONLY on these abstract interfaces, never on the concrete
infrastructure implementations. This is the Clean Architecture dependency rule:
inner layers (domain, application) must never import from outer layers (infrastructure).

Concrete implementations:
    AuditLoggerPort     → infrastructure/audit/audit_logger.py :: AuditLogger
    NotificationPort    → infrastructure/notifications/notification_service.py :: NotificationService

Constructor injection pattern used in use cases:
    class CreatePrescriptionUseCase:
        def __init__(self,
                     audit: AuditLoggerPort = None,
                     notifications: NotificationPort = None):
            self.audit         = audit         or AuditLogger()
            self.notifications = notifications or NotificationService()
"""
from abc import ABC, abstractmethod


class AuditLoggerPort(ABC):
    """Abstract audit logger — injected into use cases that need audit trails."""

    @abstractmethod
    def log(
        self,
        actor_id:    str,
        actor_role:  str,
        action:      str,
        entity_type: str,
        entity_id:   str,
        detail:      dict | None = None,
        ip_address:  str  | None = None,
    ) -> None: ...


class NotificationPort(ABC):
    """Abstract notification service — injected into use cases that send alerts."""

    @abstractmethod
    def send(
        self,
        recipient_id:      str,
        title:             str,
        message:           str,
        notification_type: str,
        entity_type:       str | None = None,
        entity_id:         str | None = None,
    ) -> None: ...

    @abstractmethod
    def send_to_role(
        self,
        role:              str,
        title:             str,
        message:           str,
        notification_type: str,
        entity_type:       str | None = None,
        entity_id:         str | None = None,
    ) -> None: ...