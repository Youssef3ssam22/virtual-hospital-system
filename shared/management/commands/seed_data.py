"""Management command to seed minimal admin data for local/dev use."""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.admin.infrastructure.orm_admin_models import Department, Ward, Bed
from apps.admin.infrastructure.orm_admin_extended import Permission, Role, SystemSettings
from apps.admin.infrastructure.orm_catalog_models import (
    LabCatalogItem,
    RadiologyCatalogItem,
    ServiceCatalogItem,
)
from shared.constants.roles import Role as RoleConstants


DEPARTMENTS = [
    {
        "name": "Inpatient",
        "code": "INP",
        "department_type": "inpatient",
        "description": "Admission, bed allocation, and inpatient clinical care.",
        "manager_name": "Inpatient Operations Manager",
        "location": "Main Building",
        "floor": "2",
        "extension_phone": "2101",
        "operating_hours": "24/7",
        "is_clinical": True,
    },
    {
        "name": "Outpatient",
        "code": "OUT",
        "department_type": "outpatient",
        "description": "Ambulatory visits, clinics, and scheduled consultations.",
        "manager_name": "Outpatient Services Manager",
        "location": "Main Building",
        "floor": "1",
        "extension_phone": "1101",
        "operating_hours": "08:00-20:00",
        "is_clinical": True,
    },
    {
        "name": "Radiology",
        "code": "RAD",
        "department_type": "radiology",
        "description": "Diagnostic imaging operations and reporting.",
        "manager_name": "Radiology Manager",
        "location": "Diagnostic Wing",
        "floor": "1",
        "extension_phone": "1205",
        "operating_hours": "24/7",
        "is_clinical": True,
    },
    {
        "name": "Nursery",
        "code": "NUR",
        "department_type": "nursery",
        "description": "Newborn care and neonatal support services.",
        "manager_name": "Nursery Supervisor",
        "location": "Maternity Wing",
        "floor": "3",
        "extension_phone": "3301",
        "operating_hours": "24/7",
        "is_clinical": True,
    },
    {
        "name": "Laboratory",
        "code": "LAB",
        "department_type": "laboratory",
        "description": "Sample processing, analysis, and result release.",
        "manager_name": "Laboratory Manager",
        "location": "Diagnostic Wing",
        "floor": "Ground",
        "extension_phone": "1201",
        "operating_hours": "24/7",
        "is_clinical": True,
    },
    {
        "name": "Pharmacy",
        "code": "PHA",
        "department_type": "pharmacy",
        "description": "Medication verification, dispensing, and stock control.",
        "manager_name": "Pharmacy Manager",
        "location": "Main Building",
        "floor": "Ground",
        "extension_phone": "1301",
        "operating_hours": "24/7",
        "is_clinical": True,
    },
    {
        "name": "Billing",
        "code": "BIL",
        "department_type": "billing",
        "description": "Invoices, payments, and insurance coordination.",
        "manager_name": "Billing Manager",
        "location": "Administration Block",
        "floor": "1",
        "extension_phone": "4101",
        "operating_hours": "08:00-17:00",
        "is_clinical": False,
    },
    {
        "name": "Administration",
        "code": "ADM",
        "department_type": "administration",
        "description": "Executive operations, governance, and master data control.",
        "manager_name": "Hospital Administrator",
        "location": "Administration Block",
        "floor": "2",
        "extension_phone": "4201",
        "operating_hours": "08:00-17:00",
        "is_clinical": False,
    },
]

WARD_TEMPLATES = [
    {
        "name": "Medical Ward",
        "code": "INP-MED",
        "type": "general",
        "department_code": "INP",
        "gender_restriction": "mixed",
        "age_group": "adult",
        "specialty": "Internal Medicine",
        "nurse_station": "Station A",
        "supports_isolation": True,
        "total_beds": 6,
    },
    {
        "name": "Intensive Care Unit",
        "code": "INP-ICU",
        "type": "icu",
        "department_code": "INP",
        "gender_restriction": "mixed",
        "age_group": "adult",
        "specialty": "Critical Care",
        "nurse_station": "ICU Station",
        "supports_isolation": True,
        "total_beds": 4,
    },
    {
        "name": "Newborn Nursery",
        "code": "NUR-NEW",
        "type": "nursery",
        "department_code": "NUR",
        "gender_restriction": "mixed",
        "age_group": "neonatal",
        "specialty": "Newborn Care",
        "nurse_station": "Nursery Desk",
        "supports_isolation": True,
        "total_beds": 4,
    },
]

ROLE_MAP = [
    {
        "code": RoleConstants.ADMIN,
        "name": "Hospital Administrator",
        "category": "administration",
        "description": "Full administrative control over hospital master data.",
    },
    {
        "code": RoleConstants.ACCOUNTANT,
        "name": "Billing Officer",
        "category": "revenue_cycle",
        "description": "Owns invoices, payments, and insurance workflows.",
    },
    {
        "code": RoleConstants.LAB_TECHNICIAN,
        "name": "Laboratory Technician",
        "category": "clinical",
        "description": "Manages specimen processing and result entry.",
    },
    {
        "code": RoleConstants.DOCTOR,
        "name": "Doctor",
        "category": "clinical",
        "description": "Clinical ordering and patient management role.",
    },
    {
        "code": RoleConstants.NURSE,
        "name": "Nurse",
        "category": "clinical",
        "description": "Nursing care, observation, and shift workflows.",
    },
    {
        "code": RoleConstants.PHARMACIST,
        "name": "Pharmacist",
        "category": "clinical",
        "description": "Medication verification, dispensing, and stock oversight.",
    },
    {
        "code": RoleConstants.RADIOLOGIST,
        "name": "Radiology Officer",
        "category": "clinical",
        "description": "Imaging scheduling, execution, and reporting support.",
    },
    {
        "code": RoleConstants.RECEPTIONIST,
        "name": "Front Desk Officer",
        "category": "operations",
        "description": "Registration and outpatient intake workflows.",
    },
]

PERMISSIONS = [
    {
        "name": "View Departments",
        "code": "ADMIN.DEPARTMENTS.VIEW",
        "module": "admin",
        "action": "view",
        "scope": "departments",
        "description": "View department master data.",
        "is_sensitive": False,
    },
    {
        "name": "Manage Departments",
        "code": "ADMIN.DEPARTMENTS.MANAGE",
        "module": "admin",
        "action": "manage",
        "scope": "departments",
        "description": "Create and update departments.",
        "is_sensitive": True,
    },
    {
        "name": "Manage Wards",
        "code": "ADMIN.WARDS.MANAGE",
        "module": "admin",
        "action": "manage",
        "scope": "wards",
        "description": "Create and maintain ward structures.",
        "is_sensitive": True,
    },
    {
        "name": "Manage Beds",
        "code": "ADMIN.BEDS.MANAGE",
        "module": "admin",
        "action": "manage",
        "scope": "beds",
        "description": "Block, release, and maintain beds.",
        "is_sensitive": True,
    },
    {
        "name": "Read Audit Logs",
        "code": "ADMIN.AUDIT.READ",
        "module": "admin",
        "action": "view",
        "scope": "audit_logs",
        "description": "Review operational and security activity logs.",
        "is_sensitive": True,
    },
    {
        "name": "Manage Roles",
        "code": "ADMIN.ROLES.MANAGE",
        "module": "admin",
        "action": "manage",
        "scope": "roles",
        "description": "Create roles and maintain permission bundles.",
        "is_sensitive": True,
    },
    {
        "name": "Assign User Roles",
        "code": "ADMIN.USER_ROLES.ASSIGN",
        "module": "admin",
        "action": "assign",
        "scope": "user_roles",
        "description": "Assign roles to hospital users.",
        "is_sensitive": True,
    },
    {
        "name": "Manage System Settings",
        "code": "ADMIN.SETTINGS.CONFIGURE",
        "module": "admin",
        "action": "configure",
        "scope": "system_settings",
        "description": "Edit hospital-wide configuration.",
        "is_sensitive": True,
    },
    {
        "name": "Manage Lab Catalog",
        "code": "ADMIN.LAB_CATALOG.MANAGE",
        "module": "admin",
        "action": "manage",
        "scope": "lab_catalog",
        "description": "Maintain the laboratory master test list.",
        "is_sensitive": False,
    },
    {
        "name": "Manage Radiology Catalog",
        "code": "ADMIN.RADIOLOGY_CATALOG.MANAGE",
        "module": "admin",
        "action": "manage",
        "scope": "radiology_catalog",
        "description": "Maintain the imaging exam catalog.",
        "is_sensitive": False,
    },
    {
        "name": "Manage Service Catalog",
        "code": "ADMIN.SERVICE_CATALOG.MANAGE",
        "module": "admin",
        "action": "manage",
        "scope": "service_catalog",
        "description": "Maintain general hospital billable services.",
        "is_sensitive": False,
    },
]

PERMISSIONS += [
    {
        "name": "Manage Permission Matrix",
        "code": "ADMIN.PERMISSIONS.MANAGE",
        "module": "admin",
        "action": "manage",
        "scope": "permissions",
        "description": "Maintain hospital permission definitions and sensitive access rules.",
        "is_sensitive": True,
    },
    {
        "name": "Manage Admin Users",
        "code": "ADMIN.USERS.MANAGE",
        "module": "admin",
        "action": "manage",
        "scope": "admin_users",
        "description": "Create and maintain administrative staff users.",
        "is_sensitive": True,
    },
    {
        "name": "Read Billing Accounts",
        "code": "BILLING.ACCOUNTS.READ",
        "module": "billing",
        "action": "view",
        "scope": "patient_accounts",
        "description": "View patient billing accounts and balances.",
        "is_sensitive": True,
    },
    {
        "name": "Manage Billing Accounts",
        "code": "BILLING.ACCOUNTS.MANAGE",
        "module": "billing",
        "action": "manage",
        "scope": "patient_accounts",
        "description": "Open and maintain patient billing accounts.",
        "is_sensitive": True,
    },
    {
        "name": "Manage Invoices",
        "code": "BILLING.INVOICES.MANAGE",
        "module": "billing",
        "action": "manage",
        "scope": "invoices",
        "description": "Create, finalize, send, cancel, and adjust invoices.",
        "is_sensitive": True,
    },
    {
        "name": "Process Payments",
        "code": "BILLING.PAYMENTS.PROCESS",
        "module": "billing",
        "action": "approve",
        "scope": "payments",
        "description": "Process and refund payments received by the hospital.",
        "is_sensitive": True,
    },
    {
        "name": "Manage Insurance Claims",
        "code": "BILLING.CLAIMS.MANAGE",
        "module": "billing",
        "action": "manage",
        "scope": "insurance_claims",
        "description": "Submit, appeal, and reconcile insurance claims.",
        "is_sensitive": True,
    },
    {
        "name": "Read Billing Reports",
        "code": "BILLING.REPORTS.READ",
        "module": "billing",
        "action": "view",
        "scope": "financial_reports",
        "description": "Review billing KPIs, collections, and receivables.",
        "is_sensitive": True,
    },
    {
        "name": "Read Lab Orders",
        "code": "LAB.ORDERS.READ",
        "module": "lab",
        "action": "view",
        "scope": "orders",
        "description": "View laboratory orders and worklists.",
        "is_sensitive": True,
    },
    {
        "name": "Create Lab Orders",
        "code": "LAB.ORDERS.CREATE",
        "module": "lab",
        "action": "create",
        "scope": "orders",
        "description": "Place laboratory orders from the active catalog.",
        "is_sensitive": True,
    },
    {
        "name": "Collect Specimens",
        "code": "LAB.SPECIMENS.COLLECT",
        "module": "lab",
        "action": "manage",
        "scope": "specimens",
        "description": "Collect, reject, and manage specimen intake.",
        "is_sensitive": True,
    },
    {
        "name": "Enter Lab Results",
        "code": "LAB.RESULTS.ENTER",
        "module": "lab",
        "action": "update",
        "scope": "results",
        "description": "Enter, amend, and queue laboratory results.",
        "is_sensitive": True,
    },
    {
        "name": "Verify Lab Results",
        "code": "LAB.RESULTS.VERIFY",
        "module": "lab",
        "action": "approve",
        "scope": "results",
        "description": "Verify laboratory results before release.",
        "is_sensitive": True,
    },
    {
        "name": "Release Lab Reports",
        "code": "LAB.REPORTS.RELEASE",
        "module": "lab",
        "action": "approve",
        "scope": "reports",
        "description": "Finalize and release verified laboratory reports.",
        "is_sensitive": True,
    },
    {
        "name": "Notify Critical Values",
        "code": "LAB.CRITICAL_VALUES.NOTIFY",
        "module": "lab",
        "action": "manage",
        "scope": "critical_values",
        "description": "Acknowledge and communicate critical laboratory values.",
        "is_sensitive": True,
    },
]

LAB_CATALOG_ITEMS = [
    {
        "code": "LAB-CBC",
        "name": "Complete Blood Count",
        "description": "Routine hematology panel for inpatient and outpatient care.",
        "department_code": "LAB",
        "specimen_type": "blood",
        "sample_container": "EDTA Tube",
        "minimum_volume_ml": "2.00",
        "default_unit": "",
        "fasting_required": False,
        "turnaround_time_minutes": 90,
        "stat_available": True,
        "processing_site": "in_house",
        "price": "180.00",
    },
    {
        "code": "LAB-GLU",
        "name": "Serum Glucose",
        "description": "Chemistry test for baseline glucose measurement.",
        "department_code": "LAB",
        "specimen_type": "serum",
        "sample_container": "Plain Tube",
        "minimum_volume_ml": "1.00",
        "default_unit": "mg/dL",
        "fasting_required": True,
        "turnaround_time_minutes": 60,
        "stat_available": True,
        "processing_site": "in_house",
        "price": "95.00",
    },
    {
        "code": "LAB-CR",
        "name": "Serum Creatinine",
        "description": "Renal function chemistry test.",
        "department_code": "LAB",
        "specimen_type": "serum",
        "sample_container": "Plain Tube",
        "minimum_volume_ml": "1.00",
        "default_unit": "mg/dL",
        "fasting_required": False,
        "turnaround_time_minutes": 75,
        "stat_available": True,
        "processing_site": "in_house",
        "price": "110.00",
    },
]

RADIOLOGY_CATALOG_ITEMS = [
    {
        "code": "RAD-CXR",
        "name": "Chest X-Ray",
        "description": "Standard two-view chest radiograph.",
        "department_code": "RAD",
        "modality": "xray",
        "body_part": "Chest",
        "contrast_required": False,
        "preparation_instructions": "Remove metallic items from chest area.",
        "duration_minutes": 15,
        "sedation_required": False,
        "uses_radiation": True,
        "report_turnaround_minutes": 120,
        "price": "350.00",
    },
    {
        "code": "RAD-ABD-US",
        "name": "Abdominal Ultrasound",
        "description": "Abdominal ultrasound for liver, gallbladder, pancreas, and kidneys.",
        "department_code": "RAD",
        "modality": "ultrasound",
        "body_part": "Abdomen",
        "contrast_required": False,
        "preparation_instructions": "Fast for 6 hours before exam.",
        "duration_minutes": 30,
        "sedation_required": False,
        "uses_radiation": False,
        "report_turnaround_minutes": 180,
        "price": "550.00",
    },
]

SERVICE_CATALOG_ITEMS = [
    {
        "code": "SRV-OPD-CONS",
        "name": "Outpatient Consultation",
        "description": "Standard ambulatory physician consultation.",
        "department_code": "OUT",
        "category": "consultation",
        "service_class": "clinical",
        "revenue_code": "5100",
        "billing_type": "fixed",
        "insurance_category": "consultation",
        "package_eligible": False,
        "requires_physician_order": False,
        "requires_result_entry": False,
        "requires_bed_assignment": False,
        "service_duration_minutes": 20,
        "price": "250.00",
    },
    {
        "code": "SRV-IP-BEDDAY",
        "name": "Inpatient Bed Day",
        "description": "Daily room and nursing accommodation charge.",
        "department_code": "INP",
        "category": "room",
        "service_class": "room_and_board",
        "revenue_code": "4100",
        "billing_type": "per_day",
        "insurance_category": "room_and_board",
        "package_eligible": False,
        "requires_physician_order": False,
        "requires_result_entry": False,
        "requires_bed_assignment": True,
        "service_duration_minutes": 1440,
        "price": "900.00",
    },
    {
        "code": "SRV-NUR-OBS",
        "name": "Nursery Observation",
        "description": "Routine newborn observation and monitoring charge.",
        "department_code": "NUR",
        "category": "nursing",
        "service_class": "clinical",
        "revenue_code": "4200",
        "billing_type": "per_day",
        "insurance_category": "nursery",
        "package_eligible": True,
        "requires_physician_order": False,
        "requires_result_entry": False,
        "requires_bed_assignment": True,
        "service_duration_minutes": 1440,
        "price": "650.00",
    },
]

SYSTEM_SETTINGS = [
    {
        "key": "HOSPITAL_NAME",
        "value": "Virtual Hospital",
        "description": "Display name for the hospital.",
        "category": "hospital_profile",
        "data_type": "string",
        "is_public": True,
        "is_sensitive": False,
    },
    {
        "key": "DEFAULT_TIMEZONE",
        "value": "Africa/Cairo",
        "description": "Default timezone used in operational screens.",
        "category": "hospital_profile",
        "data_type": "string",
        "is_public": True,
        "is_sensitive": False,
    },
    {
        "key": "BED_RELEASE_TO_CLEANING",
        "value": "true",
        "description": "Released beds move to cleaning before returning to service.",
        "category": "bed_management",
        "data_type": "boolean",
        "is_public": False,
        "is_sensitive": False,
    },
    {
        "key": "AUDIT_LOG_RETENTION_DAYS",
        "value": "365",
        "description": "Number of days to retain audit log records.",
        "category": "security",
        "data_type": "integer",
        "is_public": False,
        "is_sensitive": True,
    },
    {
        "key": "BILLING_CURRENCY",
        "value": "EGP",
        "description": "Default billing currency.",
        "category": "billing",
        "data_type": "string",
        "is_public": True,
        "is_sensitive": False,
    },
]

SYSTEM_SETTINGS += [
    {
        "key": "HOSPITAL_SHORT_NAME",
        "value": "VH",
        "description": "Short display name used on printed documents.",
        "category": "hospital_profile",
        "data_type": "string",
        "is_public": True,
        "is_sensitive": False,
    },
    {
        "key": "MRN_PREFIX",
        "value": "VH",
        "description": "Prefix used when generating medical record numbers.",
        "category": "hospital_profile",
        "data_type": "string",
        "is_public": False,
        "is_sensitive": False,
    },
    {
        "key": "MRN_DIGITS",
        "value": "8",
        "description": "Number of digits used in generated MRNs.",
        "category": "hospital_profile",
        "data_type": "integer",
        "is_public": False,
        "is_sensitive": False,
    },
    {
        "key": "BILLING_DEFAULT_DUE_DAYS",
        "value": "30",
        "description": "Default number of days before an invoice becomes due.",
        "category": "billing",
        "data_type": "integer",
        "is_public": False,
        "is_sensitive": False,
    },
    {
        "key": "BILLING_ALLOW_OVERPAYMENT",
        "value": "false",
        "description": "Allow payments higher than the current remaining balance.",
        "category": "billing",
        "data_type": "boolean",
        "is_public": False,
        "is_sensitive": True,
    },
    {
        "key": "BILLING_ROOM_CHARGE_SERVICE_CODE",
        "value": "SRV-IP-BEDDAY",
        "description": "Default service code used for inpatient room-and-board charging.",
        "category": "billing",
        "data_type": "string",
        "is_public": False,
        "is_sensitive": False,
    },
    {
        "key": "LAB_AUTO_CREATE_CRITICAL_ALERTS",
        "value": "true",
        "description": "Automatically create critical-value alerts when lab result flags are critical.",
        "category": "operations",
        "data_type": "boolean",
        "is_public": False,
        "is_sensitive": False,
    },
    {
        "key": "LAB_REQUIRE_VERIFIED_RESULTS",
        "value": "true",
        "description": "Require all lab results to be verified before final report release.",
        "category": "operations",
        "data_type": "boolean",
        "is_public": False,
        "is_sensitive": False,
    },
]


class Command(BaseCommand):
    help = "Seed real-hospital departments, permissions, settings, and shared catalogs."

    @transaction.atomic
    def handle(self, *args, **options):
        permissions = self._seed_permissions()
        self._seed_roles(permissions)
        departments = self._seed_departments()
        wards = self._seed_wards(departments)
        self._seed_beds(wards)
        self._seed_lab_catalog(departments)
        self._seed_radiology_catalog(departments)
        self._seed_service_catalog(departments)
        self._seed_system_settings()
        self.stdout.write(self.style.SUCCESS("Seed data completed."))

    def _seed_permissions(self):
        seeded = {}
        for data in PERMISSIONS:
            permission, _ = Permission.objects.update_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "module": data["module"],
                    "action": data["action"],
                    "scope": data["scope"],
                    "description": data["description"],
                    "is_sensitive": data["is_sensitive"],
                },
            )
            seeded[data["code"]] = permission
        return seeded

    def _seed_roles(self, permissions):
        role_permissions = {
            RoleConstants.ADMIN: [code for code in permissions.keys()],
            RoleConstants.ACCOUNTANT: [
                "BILLING.ACCOUNTS.READ",
                "BILLING.ACCOUNTS.MANAGE",
                "BILLING.INVOICES.MANAGE",
                "BILLING.PAYMENTS.PROCESS",
                "BILLING.CLAIMS.MANAGE",
                "BILLING.REPORTS.READ",
            ],
            RoleConstants.LAB_TECHNICIAN: [
                "LAB.ORDERS.READ",
                "LAB.SPECIMENS.COLLECT",
                "LAB.RESULTS.ENTER",
                "LAB.RESULTS.VERIFY",
                "LAB.CRITICAL_VALUES.NOTIFY",
            ],
            RoleConstants.DOCTOR: [
                "LAB.ORDERS.READ",
                "LAB.ORDERS.CREATE",
                "LAB.REPORTS.RELEASE",
                "LAB.CRITICAL_VALUES.NOTIFY",
            ],
        }
        for data in ROLE_MAP:
            role, _ = Role.objects.update_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "category": data["category"],
                    "description": data["description"],
                    "is_system_role": True,
                    "is_assignable": True,
                },
            )
            codes = role_permissions.get(data["code"], [])
            if codes:
                role.permissions.set([permissions[code] for code in codes if code in permissions])

    def _seed_departments(self):
        departments = {}
        for data in DEPARTMENTS:
            dept, _ = Department.objects.update_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "department_type": data["department_type"],
                    "description": data["description"],
                    "manager_name": data["manager_name"],
                    "location": data["location"],
                    "floor": data["floor"],
                    "extension_phone": data["extension_phone"],
                    "operating_hours": data["operating_hours"],
                    "is_clinical": data["is_clinical"],
                    "status": "active",
                },
            )
            departments[data["code"]] = dept
        return departments

    def _seed_wards(self, departments):
        wards = []
        for data in WARD_TEMPLATES:
            department = departments.get(data["department_code"])
            if not department:
                continue
            ward, _ = Ward.objects.update_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "department": department,
                    "type": data["type"],
                    "gender_restriction": data["gender_restriction"],
                    "age_group": data["age_group"],
                    "specialty": data["specialty"],
                    "nurse_station": data["nurse_station"],
                    "supports_isolation": data["supports_isolation"],
                    "total_beds": data["total_beds"],
                    "available_beds": data["total_beds"],
                    "status": "active",
                },
            )
            wards.append(ward)
        return wards

    def _seed_beds(self, wards):
        for ward in wards:
            target_beds = ward.total_beds
            existing = Bed.objects.filter(ward=ward).count()
            if existing >= target_beds:
                continue
            for idx in range(existing + 1, target_beds + 1):
                room_number = f"{ward.code.split('-')[0]}-{((idx - 1) // 2) + 1:02d}"
                bed_type = "incubator" if ward.type == "nursery" else ("icu" if ward.type == "icu" else "standard")
                bed_class = "newborn" if ward.type == "nursery" else ("critical_care" if ward.type == "icu" else "general")
                features = ["oxygen", "monitor"]
                if ward.type == "icu":
                    features.append("ventilator")
                Bed.objects.update_or_create(
                    ward=ward,
                    bed_number=f"{idx:03d}",
                    defaults={
                        "room_number": room_number,
                        "type": bed_type,
                        "bed_class": bed_class,
                        "features": features,
                        "status": "available",
                        "cleaning_status": "clean",
                    },
                )

    def _seed_lab_catalog(self, departments):
        for data in LAB_CATALOG_ITEMS:
            department = departments.get(data["department_code"])
            LabCatalogItem.objects.update_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "department": department,
                    "specimen_type": data["specimen_type"],
                    "sample_container": data["sample_container"],
                    "minimum_volume_ml": data["minimum_volume_ml"],
                    "default_unit": data["default_unit"],
                    "fasting_required": data["fasting_required"],
                    "turnaround_time_minutes": data["turnaround_time_minutes"],
                    "stat_available": data["stat_available"],
                    "processing_site": data["processing_site"],
                    "price": data["price"],
                    "is_active": True,
                },
            )

    def _seed_radiology_catalog(self, departments):
        for data in RADIOLOGY_CATALOG_ITEMS:
            department = departments.get(data["department_code"])
            RadiologyCatalogItem.objects.update_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "department": department,
                    "modality": data["modality"],
                    "body_part": data["body_part"],
                    "contrast_required": data["contrast_required"],
                    "preparation_instructions": data["preparation_instructions"],
                    "duration_minutes": data["duration_minutes"],
                    "sedation_required": data["sedation_required"],
                    "uses_radiation": data["uses_radiation"],
                    "report_turnaround_minutes": data["report_turnaround_minutes"],
                    "price": data["price"],
                    "is_active": True,
                },
            )

    def _seed_service_catalog(self, departments):
        for data in SERVICE_CATALOG_ITEMS:
            department = departments.get(data["department_code"])
            ServiceCatalogItem.objects.update_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "department": department,
                    "category": data["category"],
                    "service_class": data["service_class"],
                    "revenue_code": data["revenue_code"],
                    "billing_type": data["billing_type"],
                    "insurance_category": data["insurance_category"],
                    "package_eligible": data["package_eligible"],
                    "requires_physician_order": data["requires_physician_order"],
                    "requires_result_entry": data["requires_result_entry"],
                    "requires_bed_assignment": data["requires_bed_assignment"],
                    "service_duration_minutes": data["service_duration_minutes"],
                    "price": data["price"],
                    "is_active": True,
                },
            )

    def _seed_system_settings(self):
        for data in SYSTEM_SETTINGS:
            SystemSettings.objects.update_or_create(
                key=data["key"],
                defaults={
                    "value": data["value"],
                    "description": data["description"],
                    "category": data["category"],
                    "data_type": data["data_type"],
                    "is_public": data["is_public"],
                    "is_sensitive": data["is_sensitive"],
                },
            )
