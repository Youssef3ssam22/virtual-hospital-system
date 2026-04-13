"""Domain events for patients module."""

from dataclasses import dataclass

from shared.domain.domain_event import DomainEvent


@dataclass(frozen=True)
class PatientRegistered(DomainEvent):
    patient_id: str = ""
    mrn: str = ""


@dataclass(frozen=True)
class PatientUpdated(DomainEvent):
    patient_id: str = ""


@dataclass(frozen=True)
class PatientActivated(DomainEvent):
    patient_id: str = ""


@dataclass(frozen=True)
class PatientDeactivated(DomainEvent):
    patient_id: str = ""
