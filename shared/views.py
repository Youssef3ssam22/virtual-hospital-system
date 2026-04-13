"""shared/views.py — Health check, meta choices, and dashboard endpoints."""
from django.db import connection
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        checks = {}
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            checks["database"] = "ok"
        except Exception as e:
            checks["database"] = f"error: {e}"

        try:
            from django.core.cache import cache
            cache.set("_health_ping", "pong", timeout=5)
            checks["redis"] = "ok" if cache.get("_health_ping") == "pong" else "error: unexpected value"
        except Exception as e:
            checks["redis"] = f"error: {e}"

        if not getattr(settings, "CDSS_MOCK_MODE", True):
            try:
                from infrastructure.graph.neo4j_client import neo4j_client
                neo4j_client.verify_connectivity()
                checks["neo4j"] = "ok"
            except Exception as e:
                checks["neo4j"] = f"error: {e}"
        else:
            checks["neo4j"] = "mock_mode"

        all_ok    = all(v in ("ok", "mock_mode") for v in checks.values())
        http_code = 200 if all_ok else 503
        return Response({
            "status":    "healthy" if all_ok else "degraded",
            "timestamp": timezone.now().isoformat(),
            "version":   getattr(settings, "VERSION", "2.0.0"),
            "checks":    checks,
        }, status=http_code)


class MetaChoicesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "roles": [
                {"value": "DOCTOR",         "label": "Doctor"},
                {"value": "NURSE",          "label": "Nurse"},
                {"value": "PHARMACIST",     "label": "Pharmacist"},
                {"value": "LAB_TECHNICIAN", "label": "Lab Technician"},
                {"value": "RADIOLOGIST",    "label": "Radiologist"},
                {"value": "ACCOUNTANT",     "label": "Accountant"},
                {"value": "RECEPTIONIST",   "label": "Receptionist"},
                {"value": "ADMIN",          "label": "Administrator"},
            ],
            "genders": [
                {"value": "MALE",   "label": "Male"},
                {"value": "FEMALE", "label": "Female"},
            ],
            "blood_types": [
                {"value": t, "label": t}
                for t in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            ],
            "encounter_types": [
                {"value": "OUTPATIENT", "label": "Outpatient"},
                {"value": "INPATIENT",  "label": "Inpatient"},
            ],
            "encounter_statuses": [
                {"value": "OPEN",       "label": "Open"},
                {"value": "CLOSED",     "label": "Closed"},
                {"value": "DISCHARGED", "label": "Discharged"},
            ],
            "ward_types": [
                {"value": "GENERAL",   "label": "General Ward"},
                {"value": "ICU",       "label": "ICU"},
                {"value": "CCU",       "label": "CCU"},
                {"value": "PEDIATRIC", "label": "Pediatric"},
                {"value": "MATERNITY", "label": "Maternity"},
                {"value": "SURGICAL",  "label": "Surgical"},
            ],
            "lab_priorities": [
                {"value": "ROUTINE", "label": "Routine"},
                {"value": "URGENT",  "label": "Urgent"},
                {"value": "STAT",    "label": "STAT (Immediate)"},
            ],
            "imaging_modalities": [
                {"value": "XRAY",        "label": "X-Ray"},
                {"value": "CT",          "label": "CT Scan"},
                {"value": "MRI",         "label": "MRI"},
                {"value": "ULTRASOUND",  "label": "Ultrasound"},
                {"value": "PET",         "label": "PET Scan"},
                {"value": "MAMMOGRAPHY", "label": "Mammography"},
            ],
            "allergy_severities": [
                {"value": "MILD",     "label": "Mild"},
                {"value": "MODERATE", "label": "Moderate"},
                {"value": "SEVERE",   "label": "Severe"},
                {"value": "UNKNOWN",  "label": "Unknown"},
            ],
            "invoice_statuses": [
                {"value": "UNPAID",         "label": "Unpaid"},
                {"value": "PARTIALLY_PAID", "label": "Partially Paid"},
                {"value": "PAID",           "label": "Paid"},
                {"value": "CANCELLED",      "label": "Cancelled"},
            ],
            "claim_statuses": [
                {"value": "SUBMITTED",          "label": "Submitted"},
                {"value": "UNDER_REVIEW",       "label": "Under Review"},
                {"value": "APPROVED",           "label": "Approved"},
                {"value": "PARTIALLY_APPROVED", "label": "Partially Approved"},
                {"value": "REJECTED",           "label": "Rejected"},
            ],
            "department_types": [
                {"value": "INPATIENT",      "label": "Inpatient"},
                {"value": "OUTPATIENT",     "label": "Outpatient"},
                {"value": "RADIOLOGY",      "label": "Radiology"},
                {"value": "NURSERY",        "label": "Nursery"},
                {"value": "LABORATORY",     "label": "Laboratory"},
                {"value": "PHARMACY",       "label": "Pharmacy"},
                {"value": "BILLING",        "label": "Billing"},
                {"value": "ADMINISTRATION", "label": "Administration"},
            ],
            "doctor_specialties": [
                {"value": "GENERAL",       "label": "General Medicine"},
                {"value": "CARDIOLOGY",    "label": "Cardiology"},
                {"value": "NEUROLOGY",     "label": "Neurology"},
                {"value": "ORTHOPEDICS",   "label": "Orthopedics"},
                {"value": "PEDIATRICS",    "label": "Pediatrics"},
                {"value": "OBSTETRICS",    "label": "Obstetrics & Gynecology"},
                {"value": "SURGERY",       "label": "General Surgery"},
                {"value": "EMERGENCY",     "label": "Emergency Medicine"},
                {"value": "RADIOLOGY",     "label": "Radiology"},
                {"value": "PATHOLOGY",     "label": "Pathology"},
                {"value": "PSYCHIATRY",    "label": "Psychiatry"},
                {"value": "DERMATOLOGY",   "label": "Dermatology"},
                {"value": "OPHTHALMOLOGY", "label": "Ophthalmology"},
                {"value": "ENT",           "label": "Ear, Nose & Throat"},
                {"value": "OTHER",         "label": "Other"},
            ],
        })


class DashboardView(APIView):
    """
    GET /api/v1/dashboard/

    Returns role-appropriate summary data in a single request.
    Eliminates the 5–8 separate requests a frontend needs on page load.

    The response shape is customised per role:
    - DOCTOR:       my open encounters, pending lab results, CDSS alerts, today's schedule
    - NURSE:        active admissions in ward, overdue tasks, pending handovers
    - PHARMACIST:   pending/verified prescriptions, low stock count
    - LAB_TECHNICIAN: pending/collected orders, results awaiting verification
    - RADIOLOGIST:  ordered/performed imaging awaiting report
    - ACCOUNTANT:   unpaid invoices, pending claims, today's revenue
    - ADMIN:        KPI snapshot (beds, staff, encounters)
    - RECEPTIONIST: open encounters today, patient registrations today
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = user.role
        uid  = str(user.id)

        if role == "DOCTOR":
            return Response(self._doctor(uid))
        elif role == "NURSE":
            return Response(self._nurse(uid))
        elif role == "PHARMACIST":
            return Response(self._pharmacist())
        elif role == "LAB_TECHNICIAN":
            return Response(self._lab_tech())
        elif role == "RADIOLOGIST":
            return Response(self._radiologist())
        elif role == "ACCOUNTANT":
            return Response(self._accountant())
        elif role == "RECEPTIONIST":
            return Response(self._receptionist())
        elif role == "ADMIN":
            return Response(self._admin())
        return Response({"role": role, "message": "No dashboard configured for this role."})

    # ── Role dashboards ────────────────────────────────────────────────────────

    def _doctor(self, doctor_id: str) -> dict:
        from apps.encounters.infrastructure.orm_models import Encounter
        from apps.laboratory.infrastructure.orm_models import LabOrder
        from apps.cdss.infrastructure.orm_models import CDSSAlert
        from apps.doctor.infrastructure.orm_models import DoctorScheduleSlot
        from datetime import date

        open_encounters = list(
            Encounter.objects
            .filter(doctor_id=doctor_id, status="OPEN")
            .select_related("patient")
            .order_by("-opened_at")[:10]
            .values("id", "patient__full_name", "patient__mrn",
                    "department", "opened_at", "chief_complaint")
        )
        pending_labs = LabOrder.objects.filter(
            encounter__doctor_id=doctor_id,
            status__in=["PENDING", "COLLECTED", "RESULTED", "VERIFIED"],
        ).count()
        unread_alerts = CDSSAlert.objects.filter(
            encounter__doctor_id=doctor_id, is_read=False
        ).count()
        todays_slots = list(
            DoctorScheduleSlot.objects
            .filter(doctor_id=doctor_id, slot_date=date.today())
            .order_by("start_time")
            .values("id", "start_time", "end_time", "is_available", "booked_by_id")
        )
        return {
            "role":             "DOCTOR",
            "open_encounters":  [{
                "encounter_id":    str(e["id"]),
                "patient_name":    e["patient__full_name"],
                "patient_mrn":     e["patient__mrn"],
                "department":      e["department"],
                "opened_at":       str(e["opened_at"]),
                "chief_complaint": e["chief_complaint"],
            } for e in open_encounters],
            "open_encounter_count":  len(open_encounters),
            "pending_lab_count":     pending_labs,
            "unread_cdss_alerts":    unread_alerts,
            "todays_schedule":       [{
                "slot_id":      str(s["id"]),
                "start_time":   s["start_time"],
                "end_time":     s["end_time"],
                "is_available": s["is_available"],
                "booked":       bool(s["booked_by_id"]),
            } for s in todays_slots],
        }

    def _nurse(self, nurse_id: str) -> dict:
        from apps.inpatient.infrastructure.orm_models import Admission
        from apps.nursing.infrastructure.orm_models import NursingTask, ShiftHandover
        from django.utils import timezone

        active_admissions = list(
            Admission.objects
            .filter(status="ACTIVE")
            .select_related("patient")
            .order_by("ward", "room", "bed_number")[:20]
            .values("id", "patient__full_name", "patient__mrn",
                    "ward", "room", "bed_number", "admitted_at")
        )
        overdue_tasks = NursingTask.objects.filter(
            assigned_to_id=nurse_id,
            status="PENDING",
            due_time__lt=timezone.now(),
        ).count()
        pending_handovers = ShiftHandover.objects.filter(
            incoming_nurse_id=nurse_id
        ).order_by("-handover_time")[:3].count()

        return {
            "role":             "NURSE",
            "active_admissions": [{
                "admission_id": str(a["id"]),
                "patient_name": a["patient__full_name"],
                "patient_mrn":  a["patient__mrn"],
                "ward":         a["ward"],
                "room":         a["room"],
                "bed_number":   a["bed_number"],
                "admitted_at":  str(a["admitted_at"]),
            } for a in active_admissions],
            "active_admission_count": len(active_admissions),
            "overdue_tasks":          overdue_tasks,
            "pending_handover_count": pending_handovers,
        }

    def _pharmacist(self) -> dict:
        from apps.pharmacy.infrastructure.orm_models import Prescription, DrugStock
        from django.db.models import F
        return {
            "role":                  "PHARMACIST",
            "pending_count":         Prescription.objects.filter(status="PENDING").count(),
            "verified_count":        Prescription.objects.filter(status="VERIFIED").count(),
            "low_stock_count":       DrugStock.objects.filter(
                quantity__lte=F("reorder_level"), is_active=True
            ).count(),
            "out_of_stock_count":    DrugStock.objects.filter(
                quantity=0, is_active=True
            ).count(),
        }

    def _lab_tech(self) -> dict:
        from apps.laboratory.infrastructure.orm_models import LabOrder
        return {
            "role":               "LAB_TECHNICIAN",
            "pending_count":      LabOrder.objects.filter(status="PENDING").count(),
            "collected_count":    LabOrder.objects.filter(status="COLLECTED").count(),
            "resulted_count":     LabOrder.objects.filter(status="RESULTED").count(),
            "stat_pending_count": LabOrder.objects.filter(
                status__in=["PENDING", "COLLECTED"], priority="STAT"
            ).count(),
        }

    def _radiologist(self) -> dict:
        from apps.radiology.infrastructure.orm_models import ImagingOrder
        return {
            "role":              "RADIOLOGIST",
            "ordered_count":     ImagingOrder.objects.filter(status="ORDERED").count(),
            "scheduled_count":   ImagingOrder.objects.filter(status="SCHEDULED").count(),
            "performed_count":   ImagingOrder.objects.filter(status="PERFORMED").count(),
            "stat_pending_count": ImagingOrder.objects.filter(
                status__in=["ORDERED", "SCHEDULED", "PERFORMED"], priority="STAT"
            ).count(),
        }

    def _accountant(self) -> dict:
        from apps.billing.infrastructure.orm_models import Invoice, InsuranceClaim
        from django.db.models import Sum
        from datetime import date
        today = date.today()
        revenue = Invoice.objects.filter(
            status="PAID", updated_at__date=today
        ).aggregate(s=Sum("amount_paid"))["s"] or 0
        return {
            "role":                  "ACCOUNTANT",
            "unpaid_invoice_count":  Invoice.objects.filter(status="UNPAID").count(),
            "partial_invoice_count": Invoice.objects.filter(status="PARTIALLY_PAID").count(),
            "pending_claim_count":   InsuranceClaim.objects.filter(
                status__in=["SUBMITTED", "UNDER_REVIEW"]
            ).count(),
            "revenue_today":         float(revenue),
        }

    def _receptionist(self) -> dict:
        from apps.encounters.infrastructure.orm_models import Encounter
        from apps.patients.infrastructure.orm_models import Patient
        from datetime import date
        today = date.today()
        return {
            "role":                   "RECEPTIONIST",
            "open_encounters_today":  Encounter.objects.filter(
                opened_at__date=today, status="OPEN"
            ).count(),
            "total_encounters_today": Encounter.objects.filter(
                opened_at__date=today
            ).count(),
            "patients_registered_today": Patient.objects.filter(
                created_at__date=today
            ).count(),
        }

    def _admin(self) -> dict:
        from apps.inpatient.infrastructure.orm_models import Bed
        from apps.encounters.infrastructure.orm_models import Encounter
        from apps.authentication.infrastructure.orm_models import Staff
        from apps.pharmacy.infrastructure.orm_models import DrugStock
        from django.db.models import F
        from datetime import date
        today      = date.today()
        total_beds = Bed.objects.count()
        occupied   = Bed.objects.filter(status="OCCUPIED").count()
        return {
            "role":                  "ADMIN",
            "active_staff_count":    Staff.objects.filter(is_active=True).count(),
            "open_encounters":       Encounter.objects.filter(status="OPEN").count(),
            "encounters_today":      Encounter.objects.filter(opened_at__date=today).count(),
            "total_beds":            total_beds,
            "occupied_beds":         occupied,
            "bed_occupancy_pct":     round((occupied / total_beds * 100) if total_beds else 0, 1),
            "low_stock_drugs":       DrugStock.objects.filter(
                quantity__lte=F("reorder_level"), is_active=True
            ).count(),
        }
