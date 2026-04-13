"""Serializer mixins for role-based field visibility."""

from __future__ import annotations


class RoleBasedFieldFilterMixin:
    """Hide serializer fields unless the active role is explicitly allowed."""

    role_field_permissions: dict[str, set[str]] = {}

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        role = getattr(getattr(request, "user", None), "role", None) if request else None
        for field_name, allowed_roles in self.role_field_permissions.items():
            if field_name in fields and role not in allowed_roles:
                fields.pop(field_name)
        return fields
