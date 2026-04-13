"""Repository abstractions for patients domain."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .entities import Patient, PatientAllergy


class PatientRepository(ABC):
    """Abstract contract that application use cases depend on."""

    @abstractmethod
    def add(self, patient: Patient) -> Patient:
        raise NotImplementedError

    @abstractmethod
    def update(self, patient: Patient) -> Patient:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, patient_id: str) -> Patient | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_mrn(self, mrn: str) -> Patient | None:
        raise NotImplementedError

    @abstractmethod
    def exists_by_mrn(self, mrn: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, active_only: bool = False) -> list[Patient]:
        raise NotImplementedError

    @abstractmethod
    def add_allergy(self, allergy: PatientAllergy) -> PatientAllergy:
        raise NotImplementedError

    @abstractmethod
    def list_allergies(self, patient_id: str, *, active_only: bool = True) -> list[PatientAllergy]:
        raise NotImplementedError
