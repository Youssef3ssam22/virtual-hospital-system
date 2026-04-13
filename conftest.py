"""
conftest.py — pytest fixtures for the entire test suite.
"""
import uuid
import pytest
from django.test import Client


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def unique_id():
    return uuid.uuid4().hex[:8].upper()


# ── Departments ────────────────────────────────────────────────────────────────

@pytest.fixture
def admin_dept(db):
    from apps.authentication.infrastructure.orm_models import Department
    return Department.objects.create(
        id=uuid.uuid4(), name="Administration",
        code=f"AD{uuid.uuid4().hex[:4].upper()}", department_type="ADMINISTRATION",
    )


@pytest.fixture
def opd_dept(db):
    from apps.authentication.infrastructure.orm_models import Department
    return Department.objects.create(
        id=uuid.uuid4(), name="Outpatient",
        code=f"OP{uuid.uuid4().hex[:4].upper()}", department_type="OUTPATIENT",
    )


@pytest.fixture
def inpatient_dept(db):
    from apps.authentication.infrastructure.orm_models import Department
    return Department.objects.create(
        id=uuid.uuid4(), name="Inpatient",
        code=f"IP{uuid.uuid4().hex[:4].upper()}", department_type="INPATIENT",
    )


@pytest.fixture
def lab_dept(db):
    from apps.authentication.infrastructure.orm_models import Department
    return Department.objects.create(
        id=uuid.uuid4(), name="Laboratory",
        code=f"LB{uuid.uuid4().hex[:4].upper()}", department_type="LABORATORY",
    )


@pytest.fixture
def radiology_dept(db):
    from apps.authentication.infrastructure.orm_models import Department
    return Department.objects.create(
        id=uuid.uuid4(), name="Radiology",
        code=f"RD{uuid.uuid4().hex[:4].upper()}", department_type="RADIOLOGY",
    )


# ── Staff ──────────────────────────────────────────────────────────────────────
# create_user(staff_id, password, **extra_fields)
# client.login(username=str(user.id), ...) — USERNAME_FIELD = "id"

@pytest.fixture
def admin_user(db, admin_dept):
    from apps.authentication.infrastructure.orm_models import Staff
    staff_id = uuid.uuid4()
    return Staff.objects.create_user(
        str(staff_id), "Admin@123!",
        employee_number="EMP000001",
        full_name="System Admin",
        role="ADMIN",
        department=admin_dept,
        email="admin@hospital.com",
        phone="0500000000",
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def doctor_user(db, opd_dept):
    from apps.authentication.infrastructure.orm_models import Staff
    staff_id = uuid.uuid4()
    return Staff.objects.create_user(
        str(staff_id), "Doctor@123!",
        employee_number=f"D{uuid.uuid4().hex[:6].upper()}",
        full_name="Dr. Ahmed",
        role="DOCTOR",
        department=opd_dept,
        email=f"doctor_{uuid.uuid4().hex[:6]}@hospital.com",
        phone="0500000001",
    )


@pytest.fixture
def nurse_user(db, inpatient_dept):
    from apps.authentication.infrastructure.orm_models import Staff
    staff_id = uuid.uuid4()
    return Staff.objects.create_user(
        str(staff_id), "Nurse@123!",
        employee_number=f"N{uuid.uuid4().hex[:6].upper()}",
        full_name="Nurse Fatima",
        role="NURSE",
        department=inpatient_dept,
        email=f"nurse_{uuid.uuid4().hex[:6]}@hospital.com",
        phone="0500000002",
    )


@pytest.fixture
def pharmacist_user(db, opd_dept):
    from apps.authentication.infrastructure.orm_models import Staff
    staff_id = uuid.uuid4()
    return Staff.objects.create_user(
        str(staff_id), "Pharm@123!",
        employee_number=f"P{uuid.uuid4().hex[:6].upper()}",
        full_name="Pharmacist Ali",
        role="PHARMACIST",
        department=opd_dept,
        email=f"pharm_{uuid.uuid4().hex[:6]}@hospital.com",
        phone="0500000003",
    )


@pytest.fixture
def lab_tech_user(db, opd_dept):
    from apps.authentication.infrastructure.orm_models import Staff
    staff_id = uuid.uuid4()
    return Staff.objects.create_user(
        str(staff_id), "Lab@123!",
        employee_number=f"L{uuid.uuid4().hex[:6].upper()}",
        full_name="Lab Tech",
        role="LAB_TECHNICIAN",
        department=opd_dept,
        email=f"lab_{uuid.uuid4().hex[:6]}@hospital.com",
        phone="0500000004",
    )


@pytest.fixture
def radiologist_user(db, opd_dept):
    from apps.authentication.infrastructure.orm_models import Staff
    staff_id = uuid.uuid4()
    return Staff.objects.create_user(
        str(staff_id), "Rad@123!",
        employee_number=f"R{uuid.uuid4().hex[:6].upper()}",
        full_name="Dr. Reem Al-Rashid",
        role="RADIOLOGIST",
        department=opd_dept,
        email=f"rad_{uuid.uuid4().hex[:6]}@hospital.com",
        phone="0500000005",
    )


@pytest.fixture
def accountant_user(db, admin_dept):
    from apps.authentication.infrastructure.orm_models import Staff
    staff_id = uuid.uuid4()
    return Staff.objects.create_user(
        str(staff_id), "Acct@123!",
        employee_number=f"AC{uuid.uuid4().hex[:5].upper()}",
        full_name="Accountant Nour",
        role="ACCOUNTANT",
        department=admin_dept,
        email=f"acct_{uuid.uuid4().hex[:6]}@hospital.com",
        phone="0500000006",
    )


@pytest.fixture
def receptionist_user(db, opd_dept):
    from apps.authentication.infrastructure.orm_models import Staff
    staff_id = uuid.uuid4()
    return Staff.objects.create_user(
        str(staff_id), "Recep@123!",
        employee_number=f"RC{uuid.uuid4().hex[:5].upper()}",
        full_name="Receptionist Maya",
        role="RECEPTIONIST",
        department=opd_dept,
        email=f"recep_{uuid.uuid4().hex[:6]}@hospital.com",
        phone="0500000007",
    )


# ── Clinical data ──────────────────────────────────────────────────────────────

@pytest.fixture
def patient(db):
    from apps.patients.infrastructure.orm_models import Patient
    uid = uuid.uuid4().hex[:8]
    return Patient.objects.create(
        id=uuid.uuid4(), mrn=f"MRN{uid}",
        national_id=f"NID{uid}", full_name=f"Test Patient {uid}",
        date_of_birth="1985-06-15", gender="MALE",
        blood_type="O+", phone="0501234567",
    )


@pytest.fixture
def open_encounter(db, patient):
    from apps.encounters.infrastructure.orm_models import Encounter
    return Encounter.objects.create(
        id=uuid.uuid4(), patient=patient, encounter_type="OUTPATIENT",
        department="OPD", opened_by="system", status="OPEN",
    )


@pytest.fixture
def inpatient_encounter(db, patient):
    from apps.encounters.infrastructure.orm_models import Encounter
    return Encounter.objects.create(
        id=uuid.uuid4(), patient=patient, encounter_type="INPATIENT",
        department="IPD", opened_by="system", status="OPEN",
    )


@pytest.fixture
def available_bed(db, inpatient_dept):
    from apps.inpatient.infrastructure.orm_models import Bed
    return Bed.objects.create(
        id=uuid.uuid4(), ward="General Ward", ward_type="GENERAL",
        room="101", bed_number="A", status="AVAILABLE",
        department=inpatient_dept,
    )


@pytest.fixture
def drug_stock(db):
    from apps.pharmacy.infrastructure.orm_models import DrugStock
    uid = uuid.uuid4().hex[:6].upper()
    return DrugStock.objects.create(
        id=uuid.uuid4(), drug_code=f"AMOX{uid}",
        drug_name="Amoxicillin 500mg", category="ANTIBIOTIC",
        unit="tablet", quantity=200, reorder_level=30,
        unit_price=2.50, is_active=True,
    )


# ── Authenticated clients ──────────────────────────────────────────────────────
# USERNAME_FIELD = "id" → client.login(username=str(user.id), ...)

@pytest.fixture
def admin_client(client, admin_user):
    client.login(username=str(admin_user.id), password="Admin@123!")
    return client


@pytest.fixture
def doctor_client(client, doctor_user):
    client.login(username=str(doctor_user.id), password="Doctor@123!")
    return client


@pytest.fixture
def nurse_client(client, nurse_user):
    client.login(username=str(nurse_user.id), password="Nurse@123!")
    return client


@pytest.fixture
def pharmacist_client(client, pharmacist_user):
    client.login(username=str(pharmacist_user.id), password="Pharm@123!")
    return client


@pytest.fixture
def lab_client(client, lab_tech_user):
    client.login(username=str(lab_tech_user.id), password="Lab@123!")
    return client


@pytest.fixture
def radiologist_client(client, radiologist_user):
    client.login(username=str(radiologist_user.id), password="Rad@123!")
    return client


@pytest.fixture
def accountant_client(client, accountant_user):
    client.login(username=str(accountant_user.id), password="Acct@123!")
    return client


# ── JSON helpers ───────────────────────────────────────────────────────────────

def post_json(client, url, data):
    return client.post(url, data, content_type="application/json")


def patch_json(client, url, data=None):
    return client.patch(url, data or {}, content_type="application/json")


def put_json(client, url, data=None):
    return client.put(url, data or {}, content_type="application/json")


# ── Event bus isolation ────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clean_event_bus():
    from infrastructure.event_bus.registry import reset_event_bus
    reset_event_bus()
    yield
    reset_event_bus()