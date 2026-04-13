"""Value objects for the lab domain."""

from dataclasses import dataclass

from shared.domain.exceptions import InvalidOperation


@dataclass(frozen=True)
class TestStatus:
    """Lab test status immutable value object."""

    value: str

    VALID_STATUSES = {"PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED"}

    def __post_init__(self) -> None:
        normalized = str(self.value).strip().upper()
        if normalized not in self.VALID_STATUSES:
            raise InvalidOperation(
                f"Invalid test status '{normalized}'. "
                f"Must be one of: {', '.join(sorted(self.VALID_STATUSES))}"
            )
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value

    def is_final(self) -> bool:
        return self.value in ("COMPLETED", "CANCELLED")


@dataclass(frozen=True)
class LabTestCode:
    """Immutable lab test code value object."""

    value: str

    def __post_init__(self) -> None:
        normalized = str(self.value).strip().upper()
        if not normalized:
            raise InvalidOperation("Lab test code is required")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
