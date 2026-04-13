"""Domain events for admin module."""

from dataclasses import dataclass

from shared.domain.domain_event import DomainEvent


@dataclass(frozen=True)
class AdminUserCreated(DomainEvent):
    admin_id: str = ""
    employee_number: str = ""


@dataclass(frozen=True)
class AdminUserUpdated(DomainEvent):
    admin_id: str = ""


@dataclass(frozen=True)
class AdminUserActivated(DomainEvent):
    admin_id: str = ""


@dataclass(frozen=True)
class AdminUserDeactivated(DomainEvent):
    admin_id: str = ""
