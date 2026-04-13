"""
tests/integration/test_cdss_alerts_flow.py
CDSS allergy and drug-interaction detection across the prescription workflow.
"""
import uuid
import pytest


@pytest.mark.django_db
class TestCDSSIntegration:

    def test_allergy_alert_created_on_prescription(self, doctor_client, pharmacist_client,
                                                    open_encounter, patient):
        # Add allergy to patient
        patient.known_allergies = ["PENICILLIN"]
        patient.save()

        # Check for allergy
        check = doctor_client.post("/api/v1/cdss/check/", {
            "patient_id":    str(patient.id),
            "encounter_id":  str(open_encounter.id),
            "drug_codes":    ["AMOXICILLIN"],
            "known_allergies": ["PENICILLIN"],
        }, content_type="application/json")
        assert check.status_code == 200
        assert check.json()["count"] >= 1
        alert = check.json()["alerts"][0]
        assert alert["alert_type"] == "ALLERGY"
        assert alert["severity"] in ("MAJOR","CONTRAINDICATED")

    def test_drug_interaction_warfarin_aspirin(self, doctor_client, open_encounter, patient):
        check = doctor_client.post("/api/v1/cdss/check/", {
            "patient_id":    str(patient.id),
            "encounter_id":  str(open_encounter.id),
            "drug_codes":    ["WARFARIN","ASPIRIN"],
            "known_allergies": [],
        }, content_type="application/json")
        assert check.status_code == 200
        interactions = [a for a in check.json()["alerts"]
                        if a["alert_type"] == "DRUG_INTERACTION"]
        assert len(interactions) >= 1
        assert interactions[0]["severity"] == "MAJOR"

    def test_list_patient_alerts(self, doctor_client, open_encounter, patient):
        # Generate an alert first
        doctor_client.post("/api/v1/cdss/check/", {
            "patient_id":    str(patient.id),
            "encounter_id":  str(open_encounter.id),
            "drug_codes":    ["SSRI","TRAMADOL"],
            "known_allergies": [],
        }, content_type="application/json")

        # List alerts for this patient
        resp = doctor_client.get(f"/api/v1/cdss/alerts/?patient_id={patient.id}")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_acknowledge_alert(self, doctor_client, open_encounter, patient):
        check = doctor_client.post("/api/v1/cdss/check/", {
            "patient_id":    str(patient.id),
            "encounter_id":  str(open_encounter.id),
            "drug_codes":    ["WARFARIN","IBUPROFEN"],
            "known_allergies": [],
        }, content_type="application/json")
        alert_id = check.json()["alerts"][0]["id"]

        ack = doctor_client.patch(f"/api/v1/cdss/alerts/{alert_id}/ack/")
        assert ack.status_code == 200
        assert ack.json()["is_read"] is True
