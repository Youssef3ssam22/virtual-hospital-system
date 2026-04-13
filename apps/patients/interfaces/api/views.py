"""HTTP handlers for patient APIs."""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.permissions import IsFrontDesk

from apps.patients.application.use_cases.get_patient import GetPatientUseCase
from apps.patients.application.use_cases.manage_patient import (
    ManagePatientUseCase,
    UpdatePatientCommand,
)
from apps.patients.application.use_cases.register_patient import (
    RegisterPatientCommand,
    RegisterPatientUseCase,
)
from apps.patients.domain.entities import PatientAllergy
from apps.patients.infrastructure.repositories import DjangoPatientRepository
from apps.patients.interfaces.api.serializers import (
    PatientAllergySerializer,
    PatientRegisterSerializer,
    PatientResponseSerializer,
    PatientUpdateSerializer,
)


def _repo() -> DjangoPatientRepository:
    return DjangoPatientRepository()


def _serialize_patient(patient) -> dict:
    return {
        "id": patient.id,
        "mrn": str(patient.mrn),
        "national_id": patient.national_id,
        "full_name": patient.full_name,
        "date_of_birth": patient.date_of_birth,
        "gender": str(patient.gender),
        "blood_type": str(patient.blood_type) if patient.blood_type else None,
        "phone": patient.phone,
        "is_active": patient.is_active,
    }


class PatientListCreateView(APIView):
    """GET list patients, POST register patient."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        use_case = GetPatientUseCase(_repo())
        active_only = str(request.query_params.get("active_only", "false")).lower() == "true"
        patients = use_case.list(active_only=active_only)
        payload = [_serialize_patient(item) for item in patients]
        return Response(PatientResponseSerializer(payload, many=True).data)

    def post(self, request):
        if not IsFrontDesk().has_permission(request, self):
            return Response({"detail": "You do not have permission to perform this action."}, status=403)

        serializer = PatientRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        command = RegisterPatientCommand(
            mrn=data["mrn"],
            national_id=data["national_id"],
            full_name=data["full_name"],
            date_of_birth=data["date_of_birth"].isoformat(),
            gender=data["gender"],
            blood_type=data.get("blood_type"),
            phone=data.get("phone"),
            actor_id=str(request.user.id),
            actor_role=getattr(request.user, "role", "UNKNOWN"),
        )
        created = RegisterPatientUseCase(_repo()).execute(command)
        return Response(PatientResponseSerializer(_serialize_patient(created)).data, status=status.HTTP_201_CREATED)


class PatientDetailView(APIView):
    """GET and PATCH a single patient."""

    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id: str):
        patient = GetPatientUseCase(_repo()).by_id(patient_id)
        return Response(PatientResponseSerializer(_serialize_patient(patient)).data)

    def patch(self, request, patient_id: str):
        if not IsFrontDesk().has_permission(request, self):
            return Response({"detail": "You do not have permission to perform this action."}, status=403)

        serializer = PatientUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        command = UpdatePatientCommand(patient_id=patient_id, **serializer.validated_data)
        updated = ManagePatientUseCase(_repo()).update(command)
        return Response(PatientResponseSerializer(_serialize_patient(updated)).data)


class PatientActivationView(APIView):
    """Activate/deactivate patient endpoints."""

    permission_classes = [IsAuthenticated]

    def post(self, request, patient_id: str, action: str):
        if not IsFrontDesk().has_permission(request, self):
            return Response({"detail": "You do not have permission to perform this action."}, status=403)

        manager = ManagePatientUseCase(_repo())
        if action == "activate":
            patient = manager.activate(patient_id)
        elif action == "deactivate":
            patient = manager.deactivate(patient_id)
        else:
            return Response({"detail": "Invalid action"}, status=400)
        return Response(PatientResponseSerializer(_serialize_patient(patient)).data)


class PatientAllergyView(APIView):
    """GET/POST patient allergies."""

    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id: str):
        items = _repo().list_allergies(patient_id)
        payload = [
            {
                "id": item.id,
                "patient_id": item.patient_id,
                "allergy_code": item.allergy_code,
                "allergy_name": item.allergy_name,
                "severity": item.severity,
                "recorded_by": item.recorded_by,
                "is_active": item.is_active,
            }
            for item in items
        ]
        return Response(PatientAllergySerializer(payload, many=True).data)

    def post(self, request, patient_id: str):
        serializer = PatientAllergySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        created = _repo().add_allergy(
            PatientAllergy(
                patient_id=patient_id,
                allergy_code=data["allergy_code"],
                allergy_name=data["allergy_name"],
                severity=data["severity"],
                recorded_by=data["recorded_by"],
            )
        )
        payload = {
            "id": created.id,
            "patient_id": created.patient_id,
            "allergy_code": created.allergy_code,
            "allergy_name": created.allergy_name,
            "severity": created.severity,
            "recorded_by": created.recorded_by,
            "is_active": created.is_active,
        }
        return Response(PatientAllergySerializer(payload).data, status=status.HTTP_201_CREATED)
