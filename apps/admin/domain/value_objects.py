"""Value objects for the admin domain."""

from dataclasses import dataclass

from shared.domain.exceptions import InvalidOperation


@dataclass(frozen=True)
class AdminRole:
    """Immutable admin role value object."""

    value: str

    VALID_ROLES = {"ADMIN", "SUPER_ADMIN", "SYSTEM_ADMIN"}

    def __post_init__(self) -> None:
        normalized = str(self.value).strip().upper()
        if normalized not in self.VALID_ROLES:
            raise InvalidOperation(
                f"Invalid admin role '{normalized}'. "
                f"Must be one of: {', '.join(sorted(self.VALID_ROLES))}"
            )
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value

    def is_super_admin(self) -> bool:
        return self.value in ("SUPER_ADMIN", "SYSTEM_ADMIN")

    def is_system_admin(self) -> bool:
        return self.value == "SYSTEM_ADMIN"
