"""shared/permissions.py — Role-Based Access Control permission classes.

Usage in views:
    from shared.permissions import IsDoctor, IsNurse, IsClinician

    class PrescriptionView(APIView):
        permission_classes = [IsDoctor]          # doctors only

    class VitalsView(APIView):
        permission_classes = [IsClinician]       # doctors or nurses

IMPORTANT — DRF permission_classes takes CLASSES not instances:
    CORRECT:   permission_classes = [IsDoctor]
    INCORRECT: permission_classes = [IsDoctor()]   ← raises TypeError at runtime

Do NOT use HasRole() directly in permission_classes. Create a named subclass instead:
    class IsLabOrDoctor(HasRole):
        required_roles = (Role.LAB_TECHNICIAN, Role.DOCTOR)
"""
from rest_framework.permissions import BasePermission
from shared.constants.roles import Role


class HasRole(BasePermission):
    """Base RBAC permission. Always subclass this — never use it directly
    in permission_classes (DRF instantiates permission classes with no args,
    which is correct for subclasses but meaningless for direct HasRole() calls).
    """

    required_roles: tuple[str, ...] = ()

    def __init__(self, *roles: str):
        # Supports both patterns:
        # 1. Subclass with class attribute: class IsDoctor(HasRole): required_roles = (Role.DOCTOR,)
        # 2. Direct instantiation (only for non-DRF code): HasRole(Role.DOCTOR, Role.NURSE)
        if roles:
            self.required_roles = roles

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        user_role = getattr(request.user, "role", None)
        return user_role in self.required_roles

    def has_object_permission(self, request, view, obj) -> bool:
        return self.has_permission(request, view)


class HasPermissionCode(BasePermission):
    """Permission backed by hospital Permission, Role, and UserRole records."""

    required_permissions: tuple[str, ...] = ()
    allow_roles: tuple[str, ...] = ()
    require_all: bool = False

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        user_role = getattr(request.user, "role", None)
        if user_role in self.allow_roles:
            return True

        permission_codes = self._get_permission_codes(request.user)
        if not self.required_permissions:
            return bool(permission_codes)

        if self.require_all:
            return all(code in permission_codes for code in self.required_permissions)
        return any(code in permission_codes for code in self.required_permissions)

    def has_object_permission(self, request, view, obj) -> bool:
        return self.has_permission(request, view)

    @staticmethod
    def _get_permission_codes(user) -> set[str]:
        if hasattr(user, "permission_codes"):
            try:
                value = user.permission_codes
                return set(value() if callable(value) else value)
            except Exception:
                return set()
        return set()


# ── Single-role permission classes ────────────────────────────────────────────

class IsAdmin(HasRole):
    """Hospital administrator — staff management, department config, system settings."""
    required_roles = (Role.ADMIN,)


class CanManageAdminUsers(HasPermissionCode):
    required_permissions = ("ADMIN.USERS.MANAGE",)
    allow_roles = (Role.ADMIN,)


class CanManageDepartments(HasPermissionCode):
    required_permissions = ("ADMIN.DEPARTMENTS.MANAGE",)
    allow_roles = (Role.ADMIN,)


class CanManageWards(HasPermissionCode):
    required_permissions = ("ADMIN.WARDS.MANAGE",)
    allow_roles = (Role.ADMIN,)


class CanManageBeds(HasPermissionCode):
    required_permissions = ("ADMIN.BEDS.MANAGE",)
    allow_roles = (Role.ADMIN,)


class CanReadAuditLogs(HasPermissionCode):
    required_permissions = ("ADMIN.AUDIT.READ",)
    allow_roles = (Role.ADMIN,)


class CanManageRoles(HasPermissionCode):
    required_permissions = ("ADMIN.ROLES.MANAGE", "ADMIN.PERMISSIONS.MANAGE")
    allow_roles = (Role.ADMIN,)


class CanAssignUserRoles(HasPermissionCode):
    required_permissions = ("ADMIN.USER_ROLES.ASSIGN",)
    allow_roles = (Role.ADMIN,)


class CanManageSystemSettings(HasPermissionCode):
    required_permissions = ("ADMIN.SETTINGS.CONFIGURE",)
    allow_roles = (Role.ADMIN,)


class CanManageServiceCatalog(HasPermissionCode):
    required_permissions = ("ADMIN.SERVICE_CATALOG.MANAGE",)
    allow_roles = (Role.ADMIN,)


class CanManageLabCatalog(HasPermissionCode):
    required_permissions = ("ADMIN.LAB_CATALOG.MANAGE",)
    allow_roles = (Role.ADMIN,)


class CanManageRadiologyCatalog(HasPermissionCode):
    required_permissions = ("ADMIN.RADIOLOGY_CATALOG.MANAGE",)
    allow_roles = (Role.ADMIN,)


class IsDoctor(HasRole):
    """Licensed doctor — clinical orders, prescriptions, ward rounds, diagnoses."""
    required_roles = (Role.DOCTOR,)


class IsNurse(HasRole):
    """Registered nurse — patient assessments, care plans, vitals, handovers."""
    required_roles = (Role.NURSE,)


class IsPharmacist(HasRole):
    """Pharmacist — verify and dispense prescriptions, manage drug stock."""
    required_roles = (Role.PHARMACIST,)


class IsLabTechnician(HasRole):
    """Lab technician — specimen collection, lab order processing, results entry."""
    required_roles = (Role.LAB_TECHNICIAN,)


class CanManageLabOrders(HasPermissionCode):
    required_permissions = ("LAB.ORDERS.CREATE", "LAB.ORDERS.READ")
    allow_roles = (Role.LAB_TECHNICIAN, Role.DOCTOR, Role.ADMIN)


class CanManageLabSpecimens(HasPermissionCode):
    required_permissions = ("LAB.SPECIMENS.COLLECT",)
    allow_roles = (Role.LAB_TECHNICIAN, Role.ADMIN)


class CanManageLabResults(HasPermissionCode):
    required_permissions = ("LAB.RESULTS.ENTER",)
    allow_roles = (Role.LAB_TECHNICIAN, Role.ADMIN)


class CanVerifyLabReports(HasPermissionCode):
    required_permissions = ("LAB.RESULTS.VERIFY", "LAB.REPORTS.RELEASE")
    allow_roles = (Role.DOCTOR, Role.LAB_TECHNICIAN, Role.ADMIN)


class CanHandleCriticalValues(HasPermissionCode):
    required_permissions = ("LAB.CRITICAL_VALUES.NOTIFY",)
    allow_roles = (Role.DOCTOR, Role.LAB_TECHNICIAN, Role.ADMIN)


class IsRadiologist(HasRole):
    """Radiologist — imaging order scheduling, performing scans, reporting."""
    required_roles = (Role.RADIOLOGIST,)


class IsAccountant(HasRole):
    """Accountant — invoices, payments, insurance claims, financial reports."""
    required_roles = (Role.ACCOUNTANT,)


class CanManageBilling(HasPermissionCode):
    required_permissions = (
        "BILLING.ACCOUNTS.MANAGE",
        "BILLING.INVOICES.MANAGE",
        "BILLING.PAYMENTS.PROCESS",
        "BILLING.CLAIMS.MANAGE",
    )
    allow_roles = (Role.ACCOUNTANT, Role.ADMIN)


class CanViewBilling(HasPermissionCode):
    required_permissions = ("BILLING.ACCOUNTS.READ", "BILLING.REPORTS.READ")
    allow_roles = (Role.ACCOUNTANT, Role.ADMIN)


class IsReceptionist(HasRole):
    """Receptionist — patient registration, encounter opening, appointments."""
    required_roles = (Role.RECEPTIONIST,)


# ── Multi-role convenience classes ────────────────────────────────────────────

class IsClinician(HasRole):
    """Any clinical staff (doctor or nurse) — covers shared clinical workflows."""
    required_roles = (Role.DOCTOR, Role.NURSE)


class IsMedicalStaff(HasRole):
    """All clinical + para-clinical staff — excludes admin, billing, reception."""
    required_roles = (
        Role.DOCTOR, Role.NURSE, Role.PHARMACIST,
        Role.LAB_TECHNICIAN, Role.RADIOLOGIST,
    )


class IsFrontDesk(HasRole):
    """Reception and administration — patient intake and front-office operations."""
    required_roles = (Role.RECEPTIONIST, Role.ADMIN)


class IsBillingStaff(HasRole):
    """Staff with access to financial and billing data."""
    required_roles = (Role.ACCOUNTANT, Role.ADMIN)


class IsAdminOrDoctor(HasRole):
    """Admin or doctor — management endpoints that also need clinical context."""
    required_roles = (Role.ADMIN, Role.DOCTOR)


# ── Read-only permission ──────────────────────────────────────────────────────

class IsAuthenticatedReadOnly(BasePermission):
    """Allow safe HTTP methods (GET/HEAD/OPTIONS) to any authenticated user.

    Write operations require a role-specific permission class.
    Combine with a role class when you want: read=any staff, write=specific role.

    Example:
        class PatientListView(APIView):
            # Any staff can view patient list, only receptionists can create
            def get_permissions(self):
                if self.request.method in ("GET", "HEAD", "OPTIONS"):
                    return [IsAuthenticated()]
                return [IsReceptionist()]
    """

    SAFE_METHODS = ("GET", "HEAD", "OPTIONS")

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return request.method in self.SAFE_METHODS
