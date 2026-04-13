"""infrastructure/tasks/notifications.py — Async notification delivery.

All notification side-effects from domain events run through Celery tasks
so the HTTP thread is never blocked on DB writes for notifications.

Queue routing (configured in config/celery.py):
  notifications — all notification tasks
  cdss          — CDSS alert task (isolated, higher priority)
"""
from celery import shared_task
import logging

log = logging.getLogger("virtual_hospital.tasks.notifications")


# ── Pharmacy ──────────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=30,
             queue="notifications", name="notifications.notify_pharmacists")
def notify_pharmacists_task(self, prescription_id: str, encounter_id: str) -> None:
    """Notify all active pharmacists about a new prescription."""
    try:
        from infrastructure.notifications.notification_service import NotificationService
        NotificationService().send_to_role(
            role="PHARMACIST", title="New Prescription",
            message=f"New prescription for encounter {encounter_id}",
            notification_type="PRESCRIPTION",
            entity_type="Prescription", entity_id=prescription_id,
        )
        log.info("Notified pharmacists for prescription %s", prescription_id)
    except Exception as exc:
        log.error("notify_pharmacists_task failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30,
             queue="notifications", name="notifications.notify_nurse_dispensed")
def notify_nurse_dispensed_task(self, prescription_id: str, patient_id: str, encounter_id: str) -> None:
    """Notify nurses when medication has been dispensed."""
    try:
        from infrastructure.notifications.notification_service import NotificationService
        NotificationService().send_to_role(
            role="NURSE", title="Medication Dispensed",
            message=f"Medication dispensed for patient {patient_id}",
            notification_type="PRESCRIPTION",
            entity_type="Prescription", entity_id=prescription_id,
        )
        log.info("Notified nurses for dispensed prescription %s", prescription_id)
    except Exception as exc:
        log.error("notify_nurse_dispensed_task failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30,
             queue="notifications", name="notifications.notify_low_stock")
def notify_low_stock_task(self, drug_code: str, drug_name: str,
                          quantity: float, reorder_level: float) -> None:
    """Notify pharmacists when a drug stock falls below reorder level."""
    try:
        from infrastructure.notifications.notification_service import NotificationService
        NotificationService().send_to_role(
            role="PHARMACIST", title="Low Stock Alert",
            message=f"{drug_name} ({drug_code}) is low — only {quantity} left (reorder: {reorder_level})",
            notification_type="GENERAL",
            entity_type="DrugStock", entity_id=drug_code,
        )
        log.warning("Low stock alert sent for %s (qty: %s)", drug_code, quantity)
    except Exception as exc:
        log.error("notify_low_stock_task failed: %s", exc)
        raise self.retry(exc=exc)


# ── Laboratory ────────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=30,
             queue="notifications", name="notifications.notify_lab_technicians")
def notify_lab_technicians_task(self, lab_order_id: str, encounter_id: str) -> None:
    """Notify lab technicians about a new lab order."""
    try:
        from infrastructure.notifications.notification_service import NotificationService
        NotificationService().send_to_role(
            role="LAB_TECHNICIAN", title="New Lab Order",
            message=f"New lab order for encounter {encounter_id}",
            notification_type="LAB_RESULT",
            entity_type="LabOrder", entity_id=lab_order_id,
        )
        log.info("Notified lab technicians for order %s", lab_order_id)
    except Exception as exc:
        log.error("notify_lab_technicians_task failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30,
             queue="notifications", name="notifications.notify_doctors_lab_results")
def notify_doctors_lab_results_task(self, lab_order_id: str, encounter_id: str,
                                    has_abnormal: bool) -> None:
    """Notify doctors when lab results are published."""
    try:
        from infrastructure.notifications.notification_service import NotificationService
        suffix = " — abnormal flags detected" if has_abnormal else ""
        NotificationService().send_to_role(
            role="DOCTOR", title="Lab Results Ready",
            message=f"Lab results published for encounter {encounter_id}{suffix}",
            notification_type="LAB_RESULT",
            entity_type="LabOrder", entity_id=lab_order_id,
        )
        log.info("Notified doctors for lab order %s", lab_order_id)
    except Exception as exc:
        log.error("notify_doctors_lab_results_task failed: %s", exc)
        raise self.retry(exc=exc)


# ── Radiology ─────────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=30,
             queue="notifications", name="notifications.notify_doctors_radiology")
def notify_doctors_radiology_task(self, imaging_order_id: str, encounter_id: str) -> None:
    """Notify doctors when a radiology report is published."""
    try:
        from infrastructure.notifications.notification_service import NotificationService
        NotificationService().send_to_role(
            role="DOCTOR", title="Radiology Report Ready",
            message=f"Radiology report published for encounter {encounter_id}",
            notification_type="RADIOLOGY",
            entity_type="ImagingOrder", entity_id=imaging_order_id,
        )
        log.info("Notified doctors for radiology report %s", imaging_order_id)
    except Exception as exc:
        log.error("notify_doctors_radiology_task failed: %s", exc)
        raise self.retry(exc=exc)


# ── Inpatient ─────────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=30,
             queue="notifications", name="notifications.notify_nurses_admission")
def notify_nurses_admission_task(self, admission_id: str, ward: str) -> None:
    """Notify nurses when a new patient is admitted."""
    try:
        from infrastructure.notifications.notification_service import NotificationService
        NotificationService().send_to_role(
            role="NURSE", title="New Patient Admitted",
            message=f"Patient admitted to {ward} ward",
            notification_type="GENERAL",
            entity_type="Admission", entity_id=admission_id,
        )
        log.info("Notified nurses for admission %s", admission_id)
    except Exception as exc:
        log.error("notify_nurses_admission_task failed: %s", exc)
        raise self.retry(exc=exc)


# ── CDSS ──────────────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=30,
             queue="cdss", name="notifications.notify_cdss_alert")
def notify_cdss_alert_task(self, alert_id: str, patient_id: str, severity: str) -> None:
    """Notify clinicians about a CDSS alert (MAJOR or CONTRAINDICATED only)."""
    try:
        if severity not in ("MAJOR", "CONTRAINDICATED"):
            return
        from infrastructure.notifications.notification_service import NotificationService
        NotificationService().send_to_role(
            role="DOCTOR", title=f"CDSS Alert — {severity}",
            message=f"Clinical decision support alert for patient {patient_id}",
            notification_type="CDSS",
            entity_type="CDSSAlert", entity_id=alert_id,
        )
        log.warning("CDSS alert notification sent: %s (severity: %s)", alert_id, severity)
    except Exception as exc:
        log.error("notify_cdss_alert_task failed: %s", exc)
        raise self.retry(exc=exc)


# ── Billing (auto-billing from domain events) ─────────────────────────────────
# These are financial tasks — if they permanently fail the invoice is missing
# line items. max_retries=5 gives more chances, and on_failure logs a critical
# alert so ops can investigate and manually add the missing item.

@shared_task(bind=True, max_retries=5, default_retry_delay=60,
             queue="notifications", name="notifications.notify_billing_lab")
def notify_billing_lab_task(self, lab_order_id: str, encounter_id: str, patient_id: str) -> None:
    """Auto-add a lab billing line item when a lab order is created."""
    try:
        _add_billing_item(
            encounter_id=encounter_id, patient_id=patient_id,
            item_type="LAB", description="Laboratory Order",
            quantity=1, unit_price=50.0, entity_id=lab_order_id,
        )
        log.info("Billing item added for lab order %s", lab_order_id)
    except Exception as exc:
        log.error("notify_billing_lab_task failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=5, default_retry_delay=60,
             queue="notifications", name="notifications.notify_billing_imaging")
def notify_billing_imaging_task(self, imaging_order_id: str, encounter_id: str, patient_id: str) -> None:
    """Auto-add a radiology billing line item when an imaging order is created."""
    try:
        _add_billing_item(
            encounter_id=encounter_id, patient_id=patient_id,
            item_type="RADIOLOGY", description="Imaging Order",
            quantity=1, unit_price=150.0, entity_id=imaging_order_id,
        )
        log.info("Billing item added for imaging order %s", imaging_order_id)
    except Exception as exc:
        log.error("notify_billing_imaging_task failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=5, default_retry_delay=60,
             queue="notifications", name="notifications.notify_billing_pharmacy")
def notify_billing_pharmacy_task(self, prescription_id: str, patient_id: str, encounter_id: str) -> None:
    """Auto-add a pharmacy billing line item when medication is dispensed."""
    try:
        unit_price = 0.0
        try:
            from apps.pharmacy.infrastructure.orm_models import Prescription
            from apps.pharmacy.infrastructure.orm_models import DrugStock

            rx = Prescription.objects.get(pk=prescription_id)
            drug_codes = [item["drug_code"] for item in rx.items]

            # FIX: was calling get_by_code() in a loop — N+1 queries.
            # Now fetches all drugs in a single query.
            drugs_by_code = {
                d.drug_code: d
                for d in DrugStock.objects.filter(drug_code__in=drug_codes)
            }
            for item in rx.items:
                drug = drugs_by_code.get(item["drug_code"])
                if drug:
                    unit_price += drug.unit_price * item.get("quantity", 1)
        except Exception:
            unit_price = 0.0

        _add_billing_item(
            encounter_id=encounter_id, patient_id=patient_id,
            item_type="PHARMACY", description="Medication Dispensed",
            quantity=1, unit_price=unit_price, entity_id=prescription_id,
        )
        log.info("Billing item added for dispensed prescription %s", prescription_id)
    except Exception as exc:
        log.error("notify_billing_pharmacy_task failed: %s", exc)
        raise self.retry(exc=exc)


# ── Private helper ────────────────────────────────────────────────────────────

def _add_billing_item(encounter_id: str, patient_id: str, item_type: str,
                      description: str, quantity: int, unit_price: float,
                      entity_id: str) -> None:
    """Add a line item to the invoice for this encounter.

    Uses select_for_update() inside transaction.atomic() to prevent the race
    condition where two concurrent Celery workers both read the same invoice,
    both append to their in-memory copy, then one overwrites the other on save.
    """
    if not encounter_id:
        return
    from django.db import transaction
    from apps.billing.infrastructure.orm_models import Invoice
    try:
        with transaction.atomic():
            invoice = (
                Invoice.objects
                .select_for_update()
                .filter(encounter_id=encounter_id)
                .first()
            )
            if invoice and invoice.status not in ("PAID", "CANCELLED"):
                invoice.items.append({
                    "item_type":   item_type,
                    "description": description,
                    "quantity":    quantity,
                    "unit_price":  unit_price,
                    "entity_id":   entity_id,
                })
                invoice.save(update_fields=["items"])
    except Exception as e:
        log.error("_add_billing_item failed for encounter %s: %s", encounter_id, e)
        raise  # re-raise so the Celery task retries