"""Use cases for updating and status management of patients."""

from dataclasses import dataclass

from infrastructure.database.unit_of_work import UnitOfWork
from shared.domain.exceptions import EntityNotFound
from shared.domain.ports import AuditLoggerPort

from apps.patients.domain.events import (
    PatientActivated,
    PatientDeactivated,
    PatientUpdated,
)
from apps.patients.domain.repositories import PatientRepository


@dataclass
class UpdatePatientCommand:
    patient_id: str
    full_name: str | None = None
    phone: str | None = None
    blood_type: str | None = None
    gender: str | None = None
    actor_id: str | None = None
    actor_role: str | None = None


class ManagePatientUseCase:
    def __init__(
        self,
        repository: PatientRepository,
        uow: UnitOfWork | None = None,
        audit: AuditLoggerPort | None = None,
    ):
        self.repository = repository
        self.uow = uow or UnitOfWork()
        self.audit = audit

    def update(self, command: UpdatePatientCommand):
        patient = self.repository.get_by_id(command.patient_id)
        if not patient:
            raise EntityNotFound("Patient", command.patient_id)

        patient.update_profile(
            full_name=command.full_name,
            phone=command.phone,
            blood_type=command.blood_type,
            gender=command.gender,
        )
        saved = self.repository.update(patient)

        self.uow.collect(PatientUpdated(patient_id=saved.id))
        self.uow.commit()

        if self.audit and command.actor_id and command.actor_role:
            self.audit.log(
                actor_id=command.actor_id,
                actor_role=command.actor_role,
                action="PATIENT_UPDATED",
                entity_type="Patient",
                entity_id=saved.id,
            )
        return saved

    def deactivate(self, patient_id: str):
        patient = self.repository.get_by_id(patient_id)
        if not patient:
            raise EntityNotFound("Patient", patient_id)

        patient.deactivate()
        saved = self.repository.update(patient)
        self.uow.collect(PatientDeactivated(patient_id=saved.id))
        self.uow.commit()
        return saved

    def activate(self, patient_id: str):
        patient = self.repository.get_by_id(patient_id)
        if not patient:
            raise EntityNotFound("Patient", patient_id)

        patient.activate()
        saved = self.repository.update(patient)
        self.uow.collect(PatientActivated(patient_id=saved.id))
        self.uow.commit()
        return saved
