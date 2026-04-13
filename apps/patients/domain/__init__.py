"""Domain layer for patients module."""

from .entities import Patient, PatientAllergy
from .value_objects import MRN, BloodType, Gender
from .events import (
    PatientRegistered,
    PatientUpdated,
    PatientActivated,
    PatientDeactivated,
)

__all__ = [
    "Patient",
    "PatientAllergy",
    "MRN",
    "BloodType",
    "Gender",
    "PatientRegistered",
    "PatientUpdated",
    "PatientActivated",
    "PatientDeactivated",
]
