"""Domain events for lab module."""

from dataclasses import dataclass, field

from shared.domain.domain_event import DomainEvent


@dataclass(frozen=True)
class LabOrderCreated(DomainEvent):
    order_id: str = ""
    patient_id: str = ""
    test_codes: list = field(default_factory=list)


@dataclass(frozen=True)
class LabOrderUpdated(DomainEvent):
    order_id: str = ""


@dataclass(frozen=True)
class LabResultReported(DomainEvent):
    order_id: str = ""
    test_code: str = ""
    abnormal: bool = False
