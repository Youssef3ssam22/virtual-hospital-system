"""Value objects for the patients domain."""

from dataclasses import dataclass

from shared.domain.exceptions import InvalidOperation
from shared.utils.validators import validate_blood_type


@dataclass(frozen=True)
class MRN:
    """Medical Record Number immutable value object."""

    value: str

    def __post_init__(self) -> None:
        normalized = str(self.value).strip().upper()
        if not normalized:
            raise InvalidOperation("MRN is required")
        if len(normalized) > 32:
            raise InvalidOperation("MRN cannot exceed 32 characters")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class BloodType:
    """Validated blood type immutable value object."""

    value: str

    def __post_init__(self) -> None:
        normalized = str(self.value).strip().upper()
        object.__setattr__(self, "value", validate_blood_type(normalized))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Gender:
    """Immutable gender value object for domain constraints."""

    value: str

    def __post_init__(self) -> None:
        normalized = str(self.value).strip().upper()
        if normalized not in ("MALE", "FEMALE"):
            raise InvalidOperation("Gender must be MALE or FEMALE")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
