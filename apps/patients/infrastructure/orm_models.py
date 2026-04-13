"""Django ORM models for patients."""

import uuid

from django.db import models


class Patient(models.Model):
    GENDER_CHOICES = (
        ("MALE", "Male"),
        ("FEMALE", "Female"),
    )

    BLOOD_TYPE_CHOICES = (
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mrn = models.CharField(max_length=32, unique=True, db_index=True)
    national_id = models.CharField(max_length=32, unique=True, db_index=True)
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    known_allergies = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "patients"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.mrn})"


class PatientAllergy(models.Model):
    SEVERITY_CHOICES = (
        ("MILD", "Mild"),
        ("MODERATE", "Moderate"),
        ("SEVERE", "Severe"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="allergy_records")
    allergy_code = models.CharField(max_length=50, db_index=True)
    allergy_name = models.CharField(max_length=255)
    severity = models.CharField(max_length=12, choices=SEVERITY_CHOICES, default="MILD")
    recorded_by = models.CharField(max_length=100)
    recorded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "patient_allergies"
        indexes = [models.Index(fields=["patient", "allergy_code"]) ]
        ordering = ["-recorded_at"]

    def __str__(self) -> str:
        return f"{self.patient_id} - {self.allergy_code}"


class Encounter(models.Model):
    TYPE_CHOICES = (
        ("OP", "Outpatient"),
        ("IP", "Inpatient"),
        ("ER", "Emergency"),
    )

    STATUS_CHOICES = (
        ("planned", "Planned"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="encounters")
    department = models.ForeignKey(
        "hospital_administration.Department",
        on_delete=models.PROTECT,
        related_name="encounters",
    )
    doctor = models.ForeignKey(
        "hospital_auth.User",
        on_delete=models.PROTECT,
        related_name="encounters",
    )
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planned")
    notes = models.TextField(blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "encounters"
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["patient", "status"]),
            models.Index(fields=["department", "status"]),
            models.Index(fields=["doctor", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.patient.full_name} - {self.get_type_display()} ({self.status})"
