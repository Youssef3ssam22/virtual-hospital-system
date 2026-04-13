"""Repository abstractions for admin domain."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .entities import AdminUser


class AdminRepository(ABC):
    """Abstract contract that admin use cases depend on."""

    @abstractmethod
    def add(self, admin: AdminUser) -> AdminUser:
        raise NotImplementedError

    @abstractmethod
    def update(self, admin: AdminUser) -> AdminUser:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, admin_id: str) -> AdminUser | None:
        raise NotImplementedError

    @abstractmethod
    def exists_by_employee_number(self, employee_number: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, active_only: bool = False) -> list[AdminUser]:
        raise NotImplementedError

    @abstractmethod
    def get_config(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_audit_logs(self, *, limit: int = 100) -> list[dict]:
        raise NotImplementedError
