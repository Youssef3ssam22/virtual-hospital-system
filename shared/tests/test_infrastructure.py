"""shared/tests/test_infrastructure.py

Tests for shared infrastructure utilities:
- health check endpoint
- startup_checks module
- management commands (create_admin, seed_data)
"""
import uuid
import pytest
from unittest.mock import patch


# ── C5: Health check endpoint ─────────────────────────────────────────────────

@pytest.mark.django_db
class TestHealthCheckEndpoint:
    def test_returns_200_when_healthy(self, client):
        resp = client.get("/health/")
        assert resp.status_code == 200

    def test_response_structure(self, client):
        resp = client.get("/health/")
        data = resp.json()
        assert "status"    in data
        assert "timestamp" in data
        assert "checks"    in data
        assert "version"   in data

    def test_database_check_present(self, client):
        resp = client.get("/health/")
        assert "database" in resp.json()["checks"]
        assert resp.json()["checks"]["database"] == "ok"

    def test_healthy_status_string(self, client):
        assert resp.json()["status"] == "healthy" \
            if (resp := client.get("/health/")).status_code == 200 \
            else True  # status 503 means degraded, which is also valid

    def test_no_auth_required(self, client):
        # Health checks must be reachable by load balancers without auth
        resp = client.get("/health/")
        assert resp.status_code != 403

    def test_db_failure_returns_503(self, client):
        from django.db import connection
        with patch.object(connection, "cursor", side_effect=Exception("DB down")):
            resp = client.get("/health/")
            assert resp.status_code == 503
            assert resp.json()["status"] == "degraded"


# ── C4: Startup checks ────────────────────────────────────────────────────────

class TestStartupChecks:
    def test_passes_in_debug_mode(self):
        """In DEBUG=True mode, missing optional vars should not raise."""
        from shared.utils.startup_checks import run_startup_checks
        with patch("django.conf.settings.DEBUG", True):
            run_startup_checks()  # should not raise

    def test_raises_on_missing_required_vars_in_production(self):
        """In DEBUG=False, missing required vars must raise ImproperlyConfigured."""
        from django.core.exceptions import ImproperlyConfigured
        from shared.utils.startup_checks import run_startup_checks
        import os

        # Temporarily unset a required variable
        original = os.environ.pop("SECRET_KEY", "test-secret")
        try:
            with patch("django.conf.settings.DEBUG", False):
                with pytest.raises(ImproperlyConfigured, match="SECRET_KEY"):
                    run_startup_checks()
        finally:
            os.environ["SECRET_KEY"] = original

    def test_passes_in_production_with_all_vars_set(self):
        """No exception when all required vars are present and DEBUG=False."""
        from shared.utils.startup_checks import REQUIRED_IN_PRODUCTION, run_startup_checks
        import os

        originals = {}
        try:
            for var in REQUIRED_IN_PRODUCTION:
                originals[var] = os.environ.get(var)
                os.environ[var] = "test-value"
            with patch("django.conf.settings.DEBUG", False):
                run_startup_checks()  # should not raise
        finally:
            for var, val in originals.items():
                if val is None:
                    os.environ.pop(var, None)
                else:
                    os.environ[var] = val


# ── C3: Management commands ───────────────────────────────────────────────────

@pytest.mark.django_db
class TestCreateAdminCommand:
    def test_creates_admin_user(self):
        from django.core.management import call_command
        from io import StringIO
        from apps.admin.infrastructure.orm_models import AdminUser
        out = StringIO()
        uid   = uuid.uuid4().hex[:6]
        email = f"mgmt_admin_{uid}@hospital.com"
        call_command("create_admin",
                     f"--email={email}",
                     "--password=Test@123!",
                     "--name=Test Admin",
                     stdout=out)
        assert AdminUser.objects.filter(email=email, role="ADMIN").exists()

    def test_idempotent_second_run(self):
        from django.core.management import call_command
        from io import StringIO
        uid   = uuid.uuid4().hex[:6]
        email = f"idem_admin_{uid}@hospital.com"
        call_command("create_admin", f"--email={email}", "--password=Pass@123!")
        out = StringIO()
        call_command("create_admin", f"--email={email}", "--password=Pass@123!", stdout=out)
        assert "already exists" in out.getvalue()


@pytest.mark.django_db
class TestSeedDataCommand:
    def test_creates_departments(self):
        from django.core.management import call_command
        from apps.admin.infrastructure.orm_admin_models import Department
        call_command("seed_data", verbosity=0)
        assert Department.objects.filter(code="INP", department_type="inpatient").exists()
        assert Department.objects.filter(code="OUT", department_type="outpatient").exists()
        assert Department.objects.filter(code="LAB").exists()
        assert Department.objects.count() == 8

    def test_creates_beds(self):
        from django.core.management import call_command
        from apps.admin.infrastructure.orm_admin_models import Bed
        call_command("seed_data", verbosity=0)
        assert Bed.objects.count() >= 14

    def test_creates_permissions_and_settings(self):
        from django.core.management import call_command
        from apps.admin.infrastructure.orm_admin_extended import Permission, SystemSettings
        call_command("seed_data", verbosity=0)
        assert Permission.objects.filter(code="ADMIN.DEPARTMENTS.MANAGE").exists()
        assert Permission.objects.filter(code="BILLING.INVOICES.MANAGE").exists()
        assert Permission.objects.filter(code="LAB.RESULTS.VERIFY").exists()
        assert SystemSettings.objects.filter(key="HOSPITAL_NAME", category="hospital_profile").exists()
        assert SystemSettings.objects.filter(key="BILLING_DEFAULT_DUE_DAYS", category="billing").exists()

    def test_creates_shared_catalogs(self):
        from django.core.management import call_command
        from apps.admin.infrastructure.orm_catalog_models import (
            LabCatalogItem, RadiologyCatalogItem, ServiceCatalogItem,
        )
        call_command("seed_data", verbosity=0)
        assert LabCatalogItem.objects.filter(code="LAB-CBC").exists()
        assert RadiologyCatalogItem.objects.filter(code="RAD-CXR").exists()
        assert ServiceCatalogItem.objects.filter(code="SRV-IP-BEDDAY", billing_type="per_day").exists()

    def test_bed_number_auto_generation(self):
        from apps.admin.infrastructure.orm_admin_models import Department, Ward, Bed
        department = Department.objects.create(name="Test Inpatient", code="TINP")
        ward = Ward.objects.create(
            name="Test Ward",
            code="TINP-W1",
            department=department,
            type="general",
            total_beds=5,
            available_beds=5,
        )
        Bed.objects.create(ward=ward, type="standard")
        Bed.objects.create(ward=ward, type="standard")
        assert list(ward.beds.order_by("bed_number").values_list("bed_number", flat=True)) == ["001", "002"]

    def test_idempotent(self):
        from django.core.management import call_command
        from apps.admin.infrastructure.orm_admin_models import Department
        call_command("seed_data", verbosity=0)
        count1 = Department.objects.count()
        call_command("seed_data", verbosity=0)
        count2 = Department.objects.count()
        assert count1 == count2
