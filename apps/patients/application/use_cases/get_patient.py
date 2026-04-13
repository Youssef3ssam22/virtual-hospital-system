"""Read use cases for patient data retrieval."""

from shared.domain.exceptions import EntityNotFound

from apps.patients.domain.repositories import PatientRepository


class GetPatientUseCase:
    def __init__(self, repository: PatientRepository):
        self.repository = repository

    def by_id(self, patient_id: str):
        patient = self.repository.get_by_id(patient_id)
        if not patient:
            raise EntityNotFound("Patient", patient_id)
        return patient

    def by_mrn(self, mrn: str):
        patient = self.repository.get_by_mrn(mrn)
        if not patient:
            raise EntityNotFound("Patient", mrn)
        return patient

    def list(self, *, active_only: bool = False):
        return self.repository.list(active_only=active_only)
