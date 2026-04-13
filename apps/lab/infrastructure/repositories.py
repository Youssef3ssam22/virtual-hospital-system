"""Repository implementations for Lab."""

from __future__ import annotations

from infrastructure.database.base_repository import BaseRepository

from apps.lab.domain.entities import LabOrder as DomainLabOrder
from apps.lab.domain.entities import LabResult as DomainLabResult
from apps.lab.domain.repositories import LabOrderRepository
from apps.lab.infrastructure.orm_models import LabOrder, LabResult
from apps.patients.infrastructure.orm_models import Encounter, Patient
from shared.utils.encounters import ensure_encounter_allows_orders


class DjangoLabOrderRepository(BaseRepository, LabOrderRepository):
    """Lab order repository implementation."""

    model_class = LabOrder

    @staticmethod
    def _to_domain(model: LabOrder) -> DomainLabOrder:
        """Convert ORM model to domain entity."""
        return DomainLabOrder(
            id=str(model.id),
            patient_id=str(model.patient_id),
            encounter_id=str(model.encounter_id),
            test_codes=model.test_codes,
            ordered_by=model.ordered_by,
            status=model.status,
            priority=model.priority,
            notes=model.notes,
            is_active=model.is_active,
        )

    @staticmethod
    def _to_domain_result(model: LabResult) -> DomainLabResult:
        """Convert ORM result model to domain entity."""
        return DomainLabResult(
            id=str(model.id),
            order_id=str(model.order_id),
            test_code=model.test_code,
            test_name=model.test_name,
            result_value=model.result_value,
            unit=model.unit,
            reference_range=model.reference_range,
            abnormal=model.abnormal,
            reported_by=model.reported_by,
            is_active=model.is_active,
        )

    def add(self, order: DomainLabOrder) -> DomainLabOrder:
        """Create lab order."""
        encounter = Encounter.objects.get(id=order.encounter_id)
        ensure_encounter_allows_orders(encounter)
        model = LabOrder.objects.create(
            id=order.id,
            patient=Patient.objects.get(id=order.patient_id),
            encounter=encounter,
            test_codes=order.test_codes,
            ordered_by=order.ordered_by,
            status=str(order.status),
            priority=order.priority,
            notes=order.notes,
            is_active=order.is_active,
        )
        return self._to_domain(model)

    def update(self, order: DomainLabOrder) -> DomainLabOrder:
        """Update lab order."""
        model = LabOrder.objects.get(id=order.id)
        model.status = str(order.status)
        model.notes = order.notes
        model.is_active = order.is_active
        model.save(update_fields=["status", "notes", "is_active", "updated_at"])
        return self._to_domain(model)

    def get_by_id(self, order_id: str) -> DomainLabOrder | None:
        """Get lab order by ID."""
        model = super().get_by_id(order_id)
        return self._to_domain(model) if model else None

    def list_for_patient(self, patient_id: str) -> list[DomainLabOrder]:
        """Get all lab orders for a patient."""
        models = LabOrder.objects.filter(patient_id=patient_id, is_active=True)
        return [self._to_domain(model) for model in models]

    def list_pending(self) -> list[DomainLabOrder]:
        """Get all pending lab orders."""
        models = LabOrder.objects.filter(status="PENDING", is_active=True)
        return [self._to_domain(model) for model in models]

    def add_result(self, result: DomainLabResult) -> DomainLabResult:
        """Add test result to lab order."""
        model = LabResult.objects.create(
            id=result.id,
            order_id=result.order_id,
            encounter_id=LabOrder.objects.only("encounter_id").get(id=result.order_id).encounter_id,
            test_code=result.test_code,
            test_name=result.test_name,
            result_value=result.result_value,
            unit=result.unit,
            reference_range=result.reference_range,
            abnormal=result.abnormal,
            reported_by=result.reported_by,
            is_active=result.is_active,
        )
        return self._to_domain_result(model)

    def list_results(self, order_id: str) -> list[DomainLabResult]:
        """Get all results for a lab order."""
        models = LabResult.objects.filter(order_id=order_id, is_active=True)
        return [self._to_domain_result(model) for model in models]
