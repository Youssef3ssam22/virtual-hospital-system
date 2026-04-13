"""Use case for registering admin users."""

from dataclasses import dataclass

from infrastructure.database.unit_of_work import UnitOfWork
from shared.domain.exceptions import DuplicateEntity
from shared.domain.ports import AuditLoggerPort

from apps.admin.domain.entities import AdminUser
from apps.admin.domain.events import AdminUserCreated
from apps.admin.domain.repositories import AdminRepository


@dataclass
class RegisterAdminCommand:
    employee_number: str
    email: str
    full_name: str
    role: str  # ADMIN, SUPER_ADMIN, SYSTEM_ADMIN
    department_id: str | None = None
    phone: str | None = None
    actor_id: str | None = None
    actor_role: str | None = None


class RegisterAdminUseCase:
    def __init__(
        self,
        repository: AdminRepository,
        uow: UnitOfWork | None = None,
        audit: AuditLoggerPort | None = None,
    ):
        self.repository = repository
        self.uow = uow or UnitOfWork()
        self.audit = audit

    def execute(self, command: RegisterAdminCommand) -> AdminUser:
        if self.repository.exists_by_employee_number(command.employee_number):
            raise DuplicateEntity("Admin", command.employee_number)

        admin = AdminUser(
            employee_number=command.employee_number,
            email=command.email,
            full_name=command.full_name,
            role=command.role,
            department_id=command.department_id,
            phone=command.phone,
        )
        saved = self.repository.add(admin)

        self.uow.collect(AdminUserCreated(admin_id=saved.id, employee_number=saved.employee_number))
        self.uow.commit()

        if self.audit and command.actor_id and command.actor_role:
            self.audit.log(
                actor_id=command.actor_id,
                actor_role=command.actor_role,
                action="ADMIN_CREATED",
                entity_type="Admin",
                entity_id=saved.id,
                detail={"email": saved.email, "role": saved.role},
            )
        return saved
