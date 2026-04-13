"""Use case for registering a patient."""

from dataclasses import dataclass

from infrastructure.database.unit_of_work import UnitOfWork
from shared.domain.exceptions import DuplicateEntity
from shared.domain.ports import AuditLoggerPort

from apps.patients.domain.entities import Patient
from apps.patients.domain.events import PatientRegistered
from apps.patients.domain.repositories import PatientRepository


@dataclass
class RegisterPatientCommand:
    mrn: str
    national_id: str
    full_name: str
    date_of_birth: str
    gender: str
    blood_type: str | None = None
    phone: str | None = None
    actor_id: str | None = None
    actor_role: str | None = None


class RegisterPatientUseCase:
    def __init__(
        self,
        repository: PatientRepository,
        uow: UnitOfWork | None = None,
        audit: AuditLoggerPort | None = None,
    ):
        self.repository = repository
        self.uow = uow or UnitOfWork()
        self.audit = audit

    def execute(self, command: RegisterPatientCommand) -> Patient:
        if self.repository.exists_by_mrn(command.mrn):
            raise DuplicateEntity("Patient", command.mrn)

        patient = Patient(
            mrn=command.mrn,
            national_id=command.national_id,
            full_name=command.full_name,
            date_of_birth=command.date_of_birth,
            gender=command.gender,
            blood_type=command.blood_type,
            phone=command.phone,
        )
        saved = self.repository.add(patient)

        self.uow.collect(PatientRegistered(patient_id=saved.id, mrn=str(saved.mrn)))
        self.uow.commit()

        if self.audit and command.actor_id and command.actor_role:
            self.audit.log(
                actor_id=command.actor_id,
                actor_role=command.actor_role,
                action="PATIENT_REGISTERED",
                entity_type="Patient",
                entity_id=saved.id,
                detail={"mrn": str(saved.mrn), "full_name": saved.full_name},
            )
        return saved
