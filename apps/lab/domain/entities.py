"""Lab domain entities (pure Python, no Django imports)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from shared.domain.base_entity import BaseEntity
from shared.domain.exceptions import InvalidOperation, ConflictOperation
from shared.utils.validators import validate_required

from .value_objects import TestStatus, LabTestCode


@dataclass(kw_only=True)
class LabOrder(BaseEntity):
    """Lab test order aggregate root."""

    patient_id: str = ""
    encounter_id: str = ""
    test_codes: list[str] = field(default_factory=list)
    ordered_by: str = ""
    status: TestStatus | str = "PENDING"
    priority: str = "NORMAL"  # ROUTINE, URGENT
    notes: str | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        self.patient_id = validate_required(self.patient_id, "Patient ID")
        self.encounter_id = validate_required(self.encounter_id, "Encounter ID")
        self.ordered_by = validate_required(self.ordered_by, "Ordered by")
        if not self.test_codes:
            raise InvalidOperation("At least one test code is required")
        self.status = self.status if isinstance(self.status, TestStatus) else TestStatus(self.status)
        if self.priority not in ("ROUTINE", "URGENT"):
            raise InvalidOperation("Priority must be ROUTINE or URGENT")

    def mark_in_progress(self) -> None:
        if str(self.status) != "PENDING":
            raise ConflictOperation("Can only mark pending orders as in progress")
        self.status = TestStatus("IN_PROGRESS")

    def mark_completed(self, results: dict) -> None:
        if str(self.status) != "IN_PROGRESS":
            raise ConflictOperation("Only in-progress orders can be completed")
        self.status = TestStatus("COMPLETED")

    def cancel(self, reason: str | None = None) -> None:
        if str(self.status) == "COMPLETED":
            raise ConflictOperation("Cannot cancel completed orders")
        self.is_active = False


@dataclass(kw_only=True)
class LabResult(BaseEntity):
    """Lab test result."""

    order_id: str = ""
    test_code: str = ""
    test_name: str = ""
    result_value: str = ""
    unit: str = ""
    reference_range: str | None = None
    abnormal: bool = False
    reported_by: str = ""
    is_active: bool = True

    def __post_init__(self) -> None:
        self.order_id = validate_required(self.order_id, "Order ID")
        self.test_code = validate_required(self.test_code, "Test code").upper()
        self.test_name = validate_required(self.test_name, "Test name")
        self.reported_by = validate_required(self.reported_by, "Reported by")
