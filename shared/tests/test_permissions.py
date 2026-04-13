"""shared/tests/test_permissions.py — RBAC unit tests (no DB required)."""
import pytest
from unittest.mock import MagicMock
from shared.permissions import (
    HasRole, IsAdmin, IsDoctor, IsNurse, IsPharmacist,
    IsLabTechnician, IsRadiologist, IsAccountant, IsReceptionist,
    IsClinician, IsMedicalStaff, IsFrontDesk, IsBillingStaff,
    IsAuthenticatedReadOnly,
)
from shared.constants.roles import Role


def _req(role: str):
    user = MagicMock()
    user.is_authenticated = True
    user.role = role
    req = MagicMock()
    req.user = user
    return req


def _anon():
    user = MagicMock()
    user.is_authenticated = False
    req = MagicMock()
    req.user = user
    return req


class TestHasRoleDirect:
    def test_matching_role_allowed(self):
        p = HasRole(Role.DOCTOR, Role.NURSE)
        assert p.has_permission(_req(Role.DOCTOR), None) is True
        assert p.has_permission(_req(Role.NURSE),  None) is True

    def test_non_matching_role_denied(self):
        assert HasRole(Role.DOCTOR).has_permission(_req(Role.NURSE), None) is False

    def test_unauthenticated_denied(self):
        assert HasRole(Role.DOCTOR).has_permission(_anon(), None) is False

    def test_object_permission_mirrors_view_permission(self):
        p = HasRole(Role.ADMIN)
        assert p.has_object_permission(_req(Role.ADMIN), None, object()) is True
        assert p.has_object_permission(_req(Role.NURSE), None, object()) is False


class TestConcreteRoles:
    @pytest.mark.parametrize("cls,allow,deny", [
        (IsAdmin,         Role.ADMIN,         Role.DOCTOR),
        (IsDoctor,        Role.DOCTOR,        Role.NURSE),
        (IsNurse,         Role.NURSE,         Role.PHARMACIST),
        (IsPharmacist,    Role.PHARMACIST,     Role.NURSE),
        (IsLabTechnician, Role.LAB_TECHNICIAN, Role.RADIOLOGIST),
        (IsRadiologist,   Role.RADIOLOGIST,    Role.ACCOUNTANT),
        (IsAccountant,    Role.ACCOUNTANT,     Role.ADMIN),
        (IsReceptionist,  Role.RECEPTIONIST,   Role.DOCTOR),
    ])
    def test_each_concrete_class(self, cls, allow, deny):
        p = cls()
        assert p.has_permission(_req(allow), None) is True
        assert p.has_permission(_req(deny),  None) is False


class TestCompositeRoles:
    def test_clinician_allows_doctor_and_nurse_only(self):
        p = IsClinician()
        assert p.has_permission(_req(Role.DOCTOR), None) is True
        assert p.has_permission(_req(Role.NURSE),  None) is True
        assert p.has_permission(_req(Role.PHARMACIST), None) is False

    def test_medical_staff_covers_all_clinical_roles(self):
        p = IsMedicalStaff()
        clinical = [Role.DOCTOR, Role.NURSE, Role.PHARMACIST, Role.LAB_TECHNICIAN, Role.RADIOLOGIST]
        admin    = [Role.ADMIN, Role.RECEPTIONIST, Role.ACCOUNTANT]
        for r in clinical: assert p.has_permission(_req(r), None) is True
        for r in admin:    assert p.has_permission(_req(r), None) is False

    def test_billing_staff_covers_accountant_and_admin(self):
        p = IsBillingStaff()
        assert p.has_permission(_req(Role.ACCOUNTANT), None) is True
        assert p.has_permission(_req(Role.ADMIN),      None) is True
        assert p.has_permission(_req(Role.DOCTOR),     None) is False

    def test_front_desk(self):
        p = IsFrontDesk()
        assert p.has_permission(_req(Role.RECEPTIONIST), None) is True
        assert p.has_permission(_req(Role.ADMIN),        None) is True
        assert p.has_permission(_req(Role.NURSE),        None) is False


class TestReadOnly:
    def _req_method(self, role, method):
        req = _req(role)
        req.method = method
        return req

    def test_get_allowed_for_authenticated(self):
        p = IsAuthenticatedReadOnly()
        for r in Role.ALL:
            assert p.has_permission(self._req_method(r, "GET"), None) is True

    def test_post_denied(self):
        p = IsAuthenticatedReadOnly()
        assert p.has_permission(self._req_method(Role.DOCTOR, "POST"), None) is False

    def test_unauthenticated_get_denied(self):
        p = IsAuthenticatedReadOnly()
        user = MagicMock(); user.is_authenticated = False
        req  = MagicMock(); req.user = user; req.method = "GET"
        assert p.has_permission(req, None) is False
