"""Repository abstractions for lab domain."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .entities import LabOrder, LabResult


class LabOrderRepository(ABC):
    """Abstract contract that lab use cases depend on."""

    @abstractmethod
    def add(self, order: LabOrder) -> LabOrder:
        raise NotImplementedError

    @abstractmethod
    def update(self, order: LabOrder) -> LabOrder:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, order_id: str) -> LabOrder | None:
        raise NotImplementedError

    @abstractmethod
    def list_for_patient(self, patient_id: str) -> list[LabOrder]:
        raise NotImplementedError

    @abstractmethod
    def list_pending(self) -> list[LabOrder]:
        raise NotImplementedError

    @abstractmethod
    def add_result(self, result: LabResult) -> LabResult:
        raise NotImplementedError

    @abstractmethod
    def list_results(self, order_id: str) -> list[LabResult]:
        raise NotImplementedError
