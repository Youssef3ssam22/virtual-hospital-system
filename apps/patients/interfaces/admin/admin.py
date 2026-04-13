"""Django admin registrations for patients models."""

from django.contrib import admin

from apps.patients.infrastructure.orm_models import Patient, PatientAllergy


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("mrn", "full_name", "national_id", "gender", "is_active", "created_at")
    search_fields = ("mrn", "full_name", "national_id", "phone")
    list_filter = ("is_active", "gender", "blood_type", "created_at")
    ordering = ("-created_at",)


@admin.register(PatientAllergy)
class PatientAllergyAdmin(admin.ModelAdmin):
    list_display = ("patient", "allergy_code", "allergy_name", "severity", "is_active", "recorded_at")
    search_fields = ("patient__mrn", "patient__full_name", "allergy_code", "allergy_name")
    list_filter = ("severity", "is_active", "recorded_at")
