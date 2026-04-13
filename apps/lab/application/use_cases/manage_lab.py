"""Use cases for managing lab orders."""

from dataclasses import dataclass

from infrastructure.database.unit_of_work import UnitOfWork
from shared.domain.exceptions import EntityNotFound
from shared.domain.ports import AuditLoggerPort

from apps.lab.domain.events import LabOrderUpdated, LabResultReported
from apps.lab.domain.repositories import LabOrderRepository


class ManageLabUseCase:
    def __init__(
        self,
        repository: LabOrderRepository,
        uow: UnitOfWork | None = None,
        audit: AuditLoggerPort | None = None,
    ):
        self.repository = repository
        self.uow = uow or UnitOfWork()
        self.audit = audit

    def mark_in_progress(self, order_id: str):
        order = self.repository.get_by_id(order_id)
        if not order:
            raise EntityNotFound("LabOrder", order_id)
        order.mark_in_progress()
        saved = self.repository.update(order)
        self.uow.collect(LabOrderUpdated(order_id=saved.id))
        self.uow.commit()
        return saved

    def mark_completed(self, order_id: str, results: dict):
        order = self.repository.get_by_id(order_id)
        if not order:
            raise EntityNotFound("LabOrder", order_id)
        order.mark_completed(results)
        saved = self.repository.update(order)
        self.uow.collect(LabOrderUpdated(order_id=saved.id))
        self.uow.commit()
        return saved

    def cancel(self, order_id: str, reason: str | None = None):
        order = self.repository.get_by_id(order_id)
        if not order:
            raise EntityNotFound("LabOrder", order_id)
        order.cancel(reason)
        saved = self.repository.update(order)
        self.uow.collect(LabOrderUpdated(order_id=saved.id))
        self.uow.commit()
        return saved
