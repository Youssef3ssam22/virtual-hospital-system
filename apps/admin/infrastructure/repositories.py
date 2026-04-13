"""Django repository implementations for admin domain contracts."""

from __future__ import annotations

from infrastructure.database.base_repository import BaseRepository

from apps.admin.domain.entities import AdminUser as DomainAdminUser
from apps.admin.domain.repositories import AdminRepository
from apps.admin.domain.value_objects import AdminRole
from apps.admin.infrastructure.orm_models import AdminUser, SystemConfig


class DjangoAdminRepository(BaseRepository, AdminRepository):
    model_class = AdminUser

    @staticmethod
    def _to_domain(model: AdminUser) -> DomainAdminUser:
        return DomainAdminUser(
            id=str(model.id),
            employee_number=model.employee_number,
            email=model.email,
            full_name=model.full_name,
            role=AdminRole(model.role),
            department_id=model.department_id,
            phone=model.phone,
            is_active=model.is_active,
        )

    def add(self, admin: DomainAdminUser) -> DomainAdminUser:
        model = AdminUser.objects.create(
            id=admin.id,
            employee_number=admin.employee_number,
            email=admin.email,
            full_name=admin.full_name,
            role=str(admin.role),
            department_id=admin.department_id,
            phone=admin.phone,
            is_active=admin.is_active,
        )
        return self._to_domain(model)

    def update(self, admin: DomainAdminUser) -> DomainAdminUser:
        model = AdminUser.objects.get(id=admin.id)
        model.full_name = admin.full_name
        model.email = admin.email
        model.phone = admin.phone
        model.role = str(admin.role)
        model.is_active = admin.is_active
        model.save(update_fields=["full_name", "email", "phone", "role", "is_active", "updated_at"])
        return self._to_domain(model)

    def get_by_id(self, admin_id: str) -> DomainAdminUser | None:
        model = super().get_by_id(admin_id)
        return self._to_domain(model) if model else None

    def exists_by_employee_number(self, employee_number: str) -> bool:
        return AdminUser.objects.filter(employee_number=str(employee_number).strip().upper()).exists()

    def list(self, *, active_only: bool = False) -> list[DomainAdminUser]:
        qs = AdminUser.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        return [self._to_domain(item) for item in qs]

    def get_config(self) -> dict:
        configs = SystemConfig.objects.all().values("key", "value")
        return {item["key"]: item["value"] for item in configs}

    def get_audit_logs(self, *, limit: int = 100) -> list[dict]:
        # Placeholder - integrate with actual audit infrastructure
        return []
