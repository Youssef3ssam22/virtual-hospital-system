"""Patient domain entities (pure Python, no Django imports)."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from shared.domain.base_entity import BaseEntity
from shared.domain.exceptions import InvalidOperation
from shared.utils.validators import (
    validate_date_of_birth,
    validate_phone,
    validate_required,
)

from .value_objects import MRN, BloodType, Gender


def _parse_dob(value: date | str) -> date:
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError as exc:
        raise InvalidOperation("Date of birth must be in YYYY-MM-DD format") from exc


@dataclass(kw_only=True)
class Patient(BaseEntity):
    """Core patient aggregate root."""

    mrn: MRN | str = ""
    national_id: str = ""
    full_name: str = ""
    date_of_birth: date | str = field(default_factory=date.today)
    gender: Gender | str = ""
    blood_type: BloodType | str | None = None
    phone: str | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        self.mrn = self.mrn if isinstance(self.mrn, MRN) else MRN(self.mrn)
        self.national_id = validate_required(self.national_id, "National ID")
        self.full_name = validate_required(self.full_name, "Full name")
        self.date_of_birth = validate_date_of_birth(_parse_dob(self.date_of_birth))
        self.gender = self.gender if isinstance(self.gender, Gender) else Gender(self.gender)

        if self.blood_type:
            self.blood_type = (
                self.blood_type
                if isinstance(self.blood_type, BloodType)
                else BloodType(self.blood_type)
            )

        if self.phone:
            self.phone = validate_phone(self.phone)

    def update_profile(self, **changes: Any) -> None:
        """Apply and validate allowed mutable fields."""
        if "full_name" in changes and changes["full_name"] is not None:
            self.full_name = validate_required(changes["full_name"], "Full name")
        if "phone" in changes:
            new_phone = changes["phone"]
            self.phone = validate_phone(new_phone) if new_phone else None
        if "blood_type" in changes:
            new_blood_type = changes["blood_type"]
            self.blood_type = BloodType(new_blood_type) if new_blood_type else None
        if "gender" in changes and changes["gender"] is not None:
            self.gender = Gender(changes["gender"])

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True


@dataclass(kw_only=True)
class PatientAllergy(BaseEntity):
    """Patient allergy data as domain entity."""

    patient_id: str = ""
    allergy_code: str = ""
    allergy_name: str = ""
    severity: str = "MILD"
    recorded_by: str = ""
    is_active: bool = True

    def __post_init__(self) -> None:
        self.patient_id = validate_required(self.patient_id, "Patient ID")
        self.allergy_code = validate_required(self.allergy_code, "Allergy code").upper()
        self.allergy_name = validate_required(self.allergy_name, "Allergy name")
        self.recorded_by = validate_required(self.recorded_by, "Recorded by")
        sev = str(self.severity).strip().upper()
        if sev not in ("MILD", "MODERATE", "SEVERE"):
            raise InvalidOperation("Allergy severity must be MILD, MODERATE, or SEVERE")
        self.severity = sev
