"""Use case for creating lab orders."""

from dataclasses import dataclass

from infrastructure.database.unit_of_work import UnitOfWork
from shared.domain.ports import AuditLoggerPort

from apps.lab.domain.entities import LabOrder
from apps.lab.domain.events import LabOrderCreated
from apps.lab.domain.repositories import LabOrderRepository


@dataclass
class CreateLabOrderCommand:
    patient_id: str
    encounter_id: str
    test_codes: list[str]
    ordered_by: str
    priority: str = "ROUTINE"
    notes: str | None = None
    actor_id: str | None = None
    actor_role: str | None = None


class RegisterLabUseCase:
    def __init__(
        self,
        repository: LabOrderRepository,
        uow: UnitOfWork | None = None,
        audit: AuditLoggerPort | None = None,
    ):
        self.repository = repository
        self.uow = uow or UnitOfWork()
        self.audit = audit

    def execute(self, command: CreateLabOrderCommand) -> LabOrder:
        order = LabOrder(
            patient_id=command.patient_id,
            encounter_id=command.encounter_id,
            test_codes=command.test_codes,
            ordered_by=command.ordered_by,
            priority=command.priority,
            notes=command.notes,
        )
        saved = self.repository.add(order)
        self.uow.collect(LabOrderCreated(
            order_id=saved.id,
            patient_id=saved.patient_id,
            test_codes=saved.test_codes,
        ))
        self.uow.commit()
        if self.audit and command.actor_id and command.actor_role:
            self.audit.log(
                actor_id=command.actor_id,
                actor_role=command.actor_role,
                action="LAB_ORDER_CREATED",
                entity_type="LabOrder",
                entity_id=saved.id,
            )
        return saved
