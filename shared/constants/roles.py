"""shared/constants/roles.py — Staff role and department type constants."""


class Role:
    DOCTOR         = "DOCTOR"
    NURSE          = "NURSE"
    PHARMACIST     = "PHARMACIST"
    LAB_TECHNICIAN = "LAB_TECHNICIAN"
    RADIOLOGIST    = "RADIOLOGIST"
    ADMIN          = "ADMIN"
    RECEPTIONIST   = "RECEPTIONIST"
    ACCOUNTANT     = "ACCOUNTANT"

    # FIX: was a plain list — mutable at runtime, anyone could do
    # Role.ALL.append("CUSTOM") and silently corrupt role validation everywhere.
    # Tuple is immutable and hashable.
    ALL: tuple = (
        DOCTOR, NURSE, PHARMACIST, LAB_TECHNICIAN,
        RADIOLOGIST, ADMIN, RECEPTIONIST, ACCOUNTANT,
    )

    # Django model field choices — list of (value, display) tuples
    CHOICES: list = [(r, r) for r in ALL]


class DepartmentType:
    INPATIENT      = "INPATIENT"
    OUTPATIENT     = "OUTPATIENT"
    NURSERY        = "NURSERY"
    LABORATORY     = "LABORATORY"
    RADIOLOGY      = "RADIOLOGY"
    PHARMACY       = "PHARMACY"
    ADMINISTRATION = "ADMINISTRATION"
    BILLING        = "BILLING"

    # FIX: same mutable list issue as Role.ALL — changed to tuple
    ALL: tuple = (
        INPATIENT, OUTPATIENT, NURSERY, LABORATORY,
        RADIOLOGY, PHARMACY, ADMINISTRATION, BILLING,
    )

    CHOICES: list = [(d, d) for d in ALL]
