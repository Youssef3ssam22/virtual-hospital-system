"""Patients API routes."""

from django.urls import path

from .views import (
    PatientActivationView,
    PatientAllergyView,
    PatientDetailView,
    PatientListCreateView,
)


urlpatterns = [
    path("", PatientListCreateView.as_view(), name="patients-list-create"),
    path("<uuid:patient_id>/", PatientDetailView.as_view(), name="patients-detail"),
    path(
        "<uuid:patient_id>/<str:action>/",
        PatientActivationView.as_view(),
        name="patients-activation",
    ),
    path("<uuid:patient_id>/allergies/", PatientAllergyView.as_view(), name="patients-allergies"),
]
