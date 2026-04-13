"""Admin domain entities (pure Python, no Django imports)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from shared.domain.base_entity import BaseEntity
from shared.domain.exceptions import InvalidOperation
from shared.utils.validators import validate_email, validate_required

from .value_objects import AdminRole


@dataclass(kw_only=True)
class AdminUser(BaseEntity):
    """Admin user aggregate root."""

    employee_number: str = ""
    email: str = ""
    full_name: str = ""
    role: AdminRole | str = ""
    department_id: str | None = None
    phone: str | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        self.employee_number = validate_required(self.employee_number, "Employee number").upper()
        self.email = validate_email(self.email)
        self.full_name = validate_required(self.full_name, "Full name")
        self.role = self.role if isinstance(self.role, AdminRole) else AdminRole(self.role)

    def update_profile(self, **changes: Any) -> None:
        """Apply and validate allowed mutable fields."""
        if "full_name" in changes and changes["full_name"] is not None:
            self.full_name = validate_required(changes["full_name"], "Full name")
        if "email" in changes and changes["email"] is not None:
            self.email = validate_email(changes["email"])
        if "phone" in changes:
            self.phone = changes["phone"]
        if "role" in changes and changes["role"] is not None:
            self.role = AdminRole(changes["role"])

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True
