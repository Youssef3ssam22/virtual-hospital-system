"""Django repository implementations for patients domain contracts."""

from __future__ import annotations

from infrastructure.database.base_repository import BaseRepository

from apps.patients.domain.entities import Patient as DomainPatient
from apps.patients.domain.entities import PatientAllergy as DomainPatientAllergy
from apps.patients.domain.repositories import PatientRepository
from apps.patients.domain.value_objects import BloodType, Gender, MRN
from apps.patients.infrastructure.orm_models import Patient, PatientAllergy


class DjangoPatientRepository(BaseRepository, PatientRepository):
    model_class = Patient

    @staticmethod
    def _to_domain(model: Patient) -> DomainPatient:
        return DomainPatient(
            id=str(model.id),
            mrn=MRN(model.mrn),
            national_id=model.national_id,
            full_name=model.full_name,
            date_of_birth=model.date_of_birth,
            gender=Gender(model.gender),
            blood_type=BloodType(model.blood_type) if model.blood_type else None,
            phone=model.phone,
            is_active=model.is_active,
        )

    @staticmethod
    def _to_domain_allergy(model: PatientAllergy) -> DomainPatientAllergy:
        return DomainPatientAllergy(
            id=str(model.id),
            patient_id=str(model.patient_id),
            allergy_code=model.allergy_code,
            allergy_name=model.allergy_name,
            severity=model.severity,
            recorded_by=model.recorded_by,
            is_active=model.is_active,
        )

    def add(self, patient: DomainPatient) -> DomainPatient:
        model = Patient.objects.create(
            id=patient.id,
            mrn=str(patient.mrn),
            national_id=patient.national_id,
            full_name=patient.full_name,
            date_of_birth=patient.date_of_birth,
            gender=str(patient.gender),
            blood_type=str(patient.blood_type) if patient.blood_type else None,
            phone=patient.phone,
            is_active=patient.is_active,
        )
        return self._to_domain(model)

    def update(self, patient: DomainPatient) -> DomainPatient:
        model = Patient.objects.get(id=patient.id)
        model.full_name = patient.full_name
        model.phone = patient.phone
        model.gender = str(patient.gender)
        model.blood_type = str(patient.blood_type) if patient.blood_type else None
        model.is_active = patient.is_active
        model.save(update_fields=["full_name", "phone", "gender", "blood_type", "is_active", "updated_at"])
        return self._to_domain(model)

    def get_by_id(self, patient_id: str) -> DomainPatient | None:
        model = super().get_by_id(patient_id)
        return self._to_domain(model) if model else None

    def get_by_mrn(self, mrn: str) -> DomainPatient | None:
        model = Patient.objects.filter(mrn=str(mrn).strip().upper()).first()
        return self._to_domain(model) if model else None

    def exists_by_mrn(self, mrn: str) -> bool:
        return Patient.objects.filter(mrn=str(mrn).strip().upper()).exists()

    def list(self, *, active_only: bool = False) -> list[DomainPatient]:
        qs = Patient.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        return [self._to_domain(item) for item in qs]

    def add_allergy(self, allergy: DomainPatientAllergy) -> DomainPatientAllergy:
        model = PatientAllergy.objects.create(
            id=allergy.id,
            patient_id=allergy.patient_id,
            allergy_code=allergy.allergy_code,
            allergy_name=allergy.allergy_name,
            severity=allergy.severity,
            recorded_by=allergy.recorded_by,
            is_active=allergy.is_active,
        )
        return self._to_domain_allergy(model)

    def list_allergies(self, patient_id: str, *, active_only: bool = True) -> list[DomainPatientAllergy]:
        qs = PatientAllergy.objects.filter(patient_id=patient_id)
        if active_only:
            qs = qs.filter(is_active=True)
        return [self._to_domain_allergy(item) for item in qs]
