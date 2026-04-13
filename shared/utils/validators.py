"""shared/utils/validators.py — Common validation utilities for domain use cases.

All functions raise InvalidOperation on failure so callers get a consistent
exception that maps to HTTP 422 via the custom exception handler.
"""
import re
from datetime import date
from shared.domain.exceptions import InvalidOperation

VALID_BLOOD_TYPES = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
PHONE_RE          = re.compile(r"^\+?[\d\s\-]{7,20}$")
EMAIL_RE          = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ICD10_RE          = re.compile(r"^[A-Z]\d{2}(\.\d{1,4})?$")


def validate_email(email: str) -> str:
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        raise InvalidOperation(f"Invalid email address: {email}")
    return email


def validate_phone(phone: str) -> str:
    phone = phone.strip()
    if not PHONE_RE.match(phone):
        raise InvalidOperation(f"Invalid phone number: {phone}")
    return phone


def validate_blood_type(blood_type: str) -> str:
    if blood_type not in VALID_BLOOD_TYPES:
        raise InvalidOperation(
            f"Invalid blood type '{blood_type}'. "
            f"Must be one of: {', '.join(sorted(VALID_BLOOD_TYPES))}"
        )
    return blood_type


def validate_gender(gender: str) -> str:
    gender = gender.strip().upper()
    if gender not in ("MALE", "FEMALE"):
        raise InvalidOperation("Gender must be MALE or FEMALE")
    return gender


def validate_date_of_birth(dob: date) -> date:
    today = date.today()
    if dob >= today:
        raise InvalidOperation("Date of birth cannot be today or in the future")
    age_years = (today - dob).days / 365.25
    if age_years > 150:
        raise InvalidOperation("Date of birth is not realistic (over 150 years ago)")
    return dob


def validate_icd10_code(code: str) -> str:
    code = code.strip().upper()
    if not ICD10_RE.match(code):
        raise InvalidOperation(
            f"Invalid ICD-10 code: '{code}'. "
            f"Expected format: letter + 2 digits + optional decimal (e.g. J18.9, I10)"
        )
    return code


def validate_icd10_codes(codes: list) -> list:
    return [validate_icd10_code(c) for c in codes]


def validate_positive_amount(amount, field_name: str = "Amount") -> float:
    # FIX: was calling float(amount) without catching ValueError.
    # If amount is a non-numeric string like "abc", it raised ValueError
    # instead of InvalidOperation — inconsistent with all other validators.
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise InvalidOperation(f"{field_name} must be a number")
    if amount <= 0:
        raise InvalidOperation(f"{field_name} must be greater than zero")
    return amount


def validate_pain_score(score) -> int:
    # FIX: same issue — int(score) raised ValueError on non-numeric input
    # instead of InvalidOperation.
    try:
        score = int(score)
    except (TypeError, ValueError):
        raise InvalidOperation("Pain score must be a number between 0 and 10")
    if not (0 <= score <= 10):
        raise InvalidOperation(f"Pain score must be between 0 and 10, got {score}")
    return score


def validate_required(value, field_name: str) -> str:
    if not str(value).strip():
        raise InvalidOperation(f"{field_name} is required and cannot be blank")
    return str(value).strip()


def validate_employee_number(emp_number: str) -> str:
    """Validate and normalise an employee number to uppercase."""
    emp_number = str(emp_number).strip().upper()
    if not emp_number:
        raise InvalidOperation("Employee number is required")
    if len(emp_number) > 20:
        raise InvalidOperation("Employee number cannot exceed 20 characters")
    return emp_number