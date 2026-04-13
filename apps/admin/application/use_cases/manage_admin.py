"""Use cases for managing admin users."""

from dataclasses import dataclass

from infrastructure.database.unit_of_work import UnitOfWork
from shared.domain.exceptions import EntityNotFound
from shared.domain.ports import AuditLoggerPort

from apps.admin.domain.events import AdminUserUpdated, AdminUserDeactivated, AdminUserActivated
from apps.admin.domain.repositories import AdminRepository


@dataclass
class UpdateAdminCommand:
    admin_id: str
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    role: str | None = None
    actor_id: str | None = None
    actor_role: str | None = None


class ManageAdminUseCase:
    def __init__(
        self,
        repository: AdminRepository,
        uow: UnitOfWork | None = None,
        audit: AuditLoggerPort | None = None,
    ):
        self.repository = repository
        self.uow = uow or UnitOfWork()
        self.audit = audit

    def update(self, command: UpdateAdminCommand):
        admin = self.repository.get_by_id(command.admin_id)
        if not admin:
            raise EntityNotFound("Admin", command.admin_id)

        admin.update_profile(
            full_name=command.full_name,
            email=command.email,
            phone=command.phone,
            role=command.role,
        )
        saved = self.repository.update(admin)

        self.uow.collect(AdminUserUpdated(admin_id=saved.id))
        self.uow.commit()

        if self.audit and command.actor_id and command.actor_role:
            self.audit.log(
                actor_id=command.actor_id,
                actor_role=command.actor_role,
                action="ADMIN_UPDATED",
                entity_type="Admin",
                entity_id=saved.id,
            )
        return saved

    def deactivate(self, admin_id: str):
        admin = self.repository.get_by_id(admin_id)
        if not admin:
            raise EntityNotFound("Admin", admin_id)

        admin.deactivate()
        saved = self.repository.update(admin)
        self.uow.collect(AdminUserDeactivated(admin_id=saved.id))
        self.uow.commit()
        return saved

    def activate(self, admin_id: str):
        admin = self.repository.get_by_id(admin_id)
        if not admin:
            raise EntityNotFound("Admin", admin_id)

        admin.activate()
        saved = self.repository.update(admin)
        self.uow.collect(AdminUserActivated(admin_id=saved.id))
        self.uow.commit()
        return saved
