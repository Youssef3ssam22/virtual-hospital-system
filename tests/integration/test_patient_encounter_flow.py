"""
Integration tests: CDSS alerts for allergy and drug interactions.
"""
import uuid
import pytest


@pytest.mark.django_db
class TestCDSSIntegration:

    @pytest.fixture
    def add_allergy(self, patient):
        from apps.patients.infrastructure.orm_models import PatientAllergy
        def _add(code="PENICILLIN", name="Penicillin", severity="SEVERE"):
            return PatientAllergy.objects.create(
                id=uuid.uuid4(),
                patient=patient,
                allergy_code=code,
                allergy_name=name,
                severity=severity,
                recorded_by="system",
            )
        return _add

    def test_allergy_alert_on_prescription(self, doctor_client, add_allergy, open_encounter, patient):
        add_allergy()
        response = doctor_client.post("/api/v1/cdss/check/", {
            "patient_id": str(patient.id),
            "encounter_id": str(open_encounter.id),
            "drug_codes": ["AMOXICILLIN"],
        }, content_type="application/json")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
        alert = data["alerts"][0]
        assert alert["alert_type"] == "ALLERGY"
        assert alert["severity"] in ("MAJOR", "CONTRAINDICATED")

    def test_no_alert_when_no_allergy(self, doctor_client, open_encounter, patient):
        response = doctor_client.post("/api/v1/cdss/check/", {
            "patient_id": str(patient.id),
            "encounter_id": str(open_encounter.id),
            "drug_codes": ["PARACETAMOL"],
        }, content_type="application/json")
        assert response.status_code == 200
        assert response.json()["blocked"] is False

    def test_drug_interaction_alert(self, doctor_client, open_encounter, patient):
        response = doctor_client.post("/api/v1/cdss/check/", {
            "patient_id": str(patient.id),
            "encounter_id": str(open_encounter.id),
            "drug_codes": ["WARFARIN", "ASPIRIN"],
        }, content_type="application/json")
        assert response.status_code == 200
        data = response.json()
        types = [a["alert_type"] for a in data["alerts"]]
        assert "DRUG_INTERACTION" in types

    def test_contraindicated_blocks(self, doctor_client, open_encounter, patient):
        response = doctor_client.post("/api/v1/cdss/check/", {
            "patient_id": str(patient.id),
            "encounter_id": str(open_encounter.id),
            "drug_codes": ["SSRI", "LINEZOLID"],
        }, content_type="application/json")
        assert response.status_code == 200
        assert response.json()["blocked"] is True

    def test_alert_is_persisted(self, doctor_client, add_allergy, open_encounter, patient):
        add_allergy()
        doctor_client.post("/api/v1/cdss/check/", {
            "patient_id": str(patient.id),
            "encounter_id": str(open_encounter.id),
            "drug_codes": ["AMOXICILLIN"],
        }, content_type="application/json")
        from apps.cdss.infrastructure.orm_models import CDSSAlert
        assert CDSSAlert.objects.filter(patient_id=patient.id).exists()

    def test_acknowledge_alert(self, doctor_client, add_allergy, open_encounter, patient):
        add_allergy()
        doctor_client.post("/api/v1/cdss/check/", {
            "patient_id": str(patient.id),
            "encounter_id": str(open_encounter.id),
            "drug_codes": ["AMOXICILLIN"],
        }, content_type="application/json")
        from apps.cdss.infrastructure.orm_models import CDSSAlert
        alert = CDSSAlert.objects.filter(patient_id=patient.id).first()
        ack = doctor_client.patch(f"/api/v1/cdss/alerts/{alert.id}/ack/")
        assert ack.status_code == 200
        assert ack.json()["is_read"] is True
