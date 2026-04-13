"""Billing workflow services."""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.admin.infrastructure.orm_admin_models import BedAssignment
from apps.admin.infrastructure.orm_catalog_models import LabCatalogItem, ServiceCatalogItem
from apps.billing.infrastructure.orm_billing_models import (
    FinancialTimeline,
    InsuranceClaim,
    Invoice,
    InvoiceLineItem,
    PatientAccount,
    Payment,
    Transaction,
)
from apps.lab.infrastructure.orm_models import LabResult
from shared.utils.encounters import ensure_encounter_billable, ensure_encounter_closed_for_final_billing
from shared.utils.state_machines import InvalidTransitionError, ensure_transition
from shared.utils.notifications import emit_event


INVOICE_TRANSITIONS = {
    "draft": {"issued", "void", "cancelled"},
    "issued": {"sent", "partially_paid", "fully_paid", "void", "cancelled", "overdue"},
    "sent": {"viewed", "partially_paid", "fully_paid", "void", "cancelled", "overdue"},
    "viewed": {"partially_paid", "fully_paid", "void", "cancelled", "overdue"},
    "partially_paid": {"fully_paid", "void"},
    "overdue": {"partially_paid", "fully_paid", "void"},
    "fully_paid": set(),
    "void": set(),
    "cancelled": set(),
}

CLAIM_TRANSITIONS = {
    "draft": {"submitted"},
    "submitted": {"pending", "rejected", "approved", "resubmitted"},
    "pending": {"approved", "rejected", "paid", "resubmitted"},
    "approved": {"paid", "resubmitted"},
    "rejected": {"resubmitted"},
    "resubmitted": {"pending", "approved", "rejected", "paid"},
    "paid": set(),
    "appealed": {"pending", "approved", "rejected"},
}


def assert_invoice_transition(invoice: Invoice, new_status: str) -> None:
    ensure_transition(invoice.status, new_status, INVOICE_TRANSITIONS, "invoice")


def assert_claim_transition(claim: InsuranceClaim, new_status: str) -> None:
    ensure_transition(claim.status, new_status, CLAIM_TRANSITIONS, "claim")


@transaction.atomic
def sync_invoice_totals(invoice: Invoice, actor_id: str = "system") -> Invoice:
    locked_invoice = Invoice.objects.select_for_update().select_related("account", "encounter").get(pk=invoice.pk)
    previous_total = locked_invoice.total_amount
    locked_invoice.recompute_totals()
    if locked_invoice.encounter_id:
        ensure_encounter_billable(locked_invoice.encounter)
    locked_invoice.save(update_fields=["subtotal", "total_amount", "remaining_balance", "updated_at"])
    delta = locked_invoice.total_amount - previous_total
    if delta != Decimal("0.00"):
        _record_transaction(
            account=locked_invoice.account,
            invoice=locked_invoice,
            transaction_type="charge" if delta > 0 else "adjustment",
            amount=abs(delta),
            reference_id=str(locked_invoice.id),
            actor_id=actor_id,
            metadata={
                "invoice_number": locked_invoice.invoice_number,
                "previous_total": str(previous_total),
                "new_total": str(locked_invoice.total_amount),
            },
        )
    _record_timeline(
        account=locked_invoice.account,
        transaction_type="invoice",
        reference_id=str(locked_invoice.id),
        amount=locked_invoice.total_amount,
        balance_after=locked_invoice.remaining_balance,
        description=f"Invoice {locked_invoice.invoice_number} recalculated",
        recorded_by=actor_id,
        metadata={"invoice_number": locked_invoice.invoice_number},
    )
    return locked_invoice


@transaction.atomic
def apply_payment(payment: Payment, actor_id: str = "system") -> Payment:
    payment = Payment.objects.select_for_update().select_related("account", "invoice", "patient").get(pk=payment.pk)
    if payment.status != "pending":
        raise InvalidTransitionError("Only pending payments can be processed.")
    account = PatientAccount.objects.select_for_update().get(pk=payment.account_id)
    account.recompute_balances()
    if payment.payment_amount <= 0:
        raise InvalidTransitionError("Payment amount must be positive.")
    if payment.invoice:
        invoice = Invoice.objects.select_for_update().select_related("encounter").get(pk=payment.invoice_id)
        if invoice.encounter_id:
            ensure_encounter_billable(invoice.encounter)
    else:
        invoice = None
    if invoice and payment.payment_amount > invoice.remaining_balance:
        raise InvalidTransitionError("Payment amount cannot exceed invoice remaining balance.")

    payment.status = "processed"
    payment.recorded_by = actor_id
    payment.save(update_fields=["status", "recorded_by", "updated_at"])

    if invoice:
        invoice.paid_amount += payment.payment_amount
        invoice.recompute_totals()
        invoice.status = "fully_paid" if invoice.remaining_balance == Decimal("0.00") else "partially_paid"
        invoice.save(update_fields=["paid_amount", "subtotal", "total_amount", "remaining_balance", "status", "updated_at"])

    account.recompute_balances()
    account.save(update_fields=["total_balance", "total_paid", "updated_at"])
    _record_transaction(
        account=account,
        invoice=invoice,
        payment=payment,
        transaction_type="payment",
        amount=payment.payment_amount,
        reference_id=str(payment.id),
        actor_id=actor_id,
        metadata={"invoice_id": str(invoice.id) if invoice else None},
    )

    _record_timeline(
        account=account,
        transaction_type="payment",
        reference_id=str(payment.id),
        amount=payment.payment_amount,
        balance_after=account.total_balance,
        description=f"Payment {payment.reference_number or payment.id}",
        recorded_by=actor_id,
        metadata={"invoice_id": str(payment.invoice_id) if payment.invoice_id else None},
    )
    emit_event(
        "billing",
        "payment_received",
        {
            "payment_id": str(payment.id),
            "invoice_id": str(payment.invoice_id) if payment.invoice_id else None,
            "patient_id": str(payment.patient_id),
            "amount": str(payment.payment_amount),
        },
    )
    return payment


def _record_timeline(
    *,
    account: PatientAccount,
    transaction_type: str,
    reference_id: str,
    amount,
    balance_after,
    description: str,
    recorded_by: str,
    metadata: dict | None = None,
) -> None:
    FinancialTimeline.objects.create(
        account=account,
        transaction_type=transaction_type,
        reference_id=reference_id,
        amount=amount,
        balance_after=balance_after,
        description=description,
        recorded_by=recorded_by,
        metadata=metadata or {},
    )


def _record_transaction(
    *,
    account: PatientAccount,
    transaction_type: str,
    amount,
    reference_id: str,
    actor_id: str,
    invoice: Invoice | None = None,
    payment: Payment | None = None,
    metadata: dict | None = None,
) -> Transaction:
    return Transaction.objects.create(
        account=account,
        invoice=invoice,
        payment=payment,
        type=transaction_type,
        amount=amount,
        reference_id=reference_id,
        created_by=actor_id,
        metadata=metadata or {},
    )


def record_adjustment(
    *,
    account: PatientAccount,
    invoice: Invoice | None,
    amount,
    reference_id: str,
    actor_id: str,
    metadata: dict | None = None,
) -> Transaction:
    return _record_transaction(
        account=account,
        invoice=invoice,
        transaction_type="adjustment",
        amount=amount,
        reference_id=reference_id,
        actor_id=actor_id,
        metadata=metadata,
    )


@transaction.atomic
def auto_create_invoice_item_from_lab_result(result: LabResult, actor_id: str = "system") -> InvoiceLineItem | None:
    if result.status != "verified":
        return None
    catalog_item = LabCatalogItem.objects.filter(code__iexact=result.test_code, is_active=True).first()
    if catalog_item is None:
        return None
    account = _get_or_create_account(result.order.patient, actor_id=actor_id)
    invoice = _get_or_create_open_invoice(account=account, encounter=result.order.encounter, actor_id=actor_id)
    if invoice.line_items.filter(source_type="lab", source_id=str(result.id), archived_at__isnull=True).exists():
        return None
    line_item = InvoiceLineItem.objects.create(
        invoice=invoice,
        item_type="lab",
        description=catalog_item.name,
        lab_catalog_item=catalog_item,
        quantity=Decimal("1.00"),
        unit_price=catalog_item.price,
        total_price=catalog_item.price,
        service_code=catalog_item.code,
        cpt_code=getattr(catalog_item, "billing_code", "") or catalog_item.code,
        provider=result.verified_by or result.reported_by,
        service_date=result.verified_at or result.reported_at,
        source_type="lab",
        source_id=str(result.id),
    )
    sync_invoice_totals(invoice, actor_id=actor_id)
    emit_event(
        "billing",
        "invoice_created",
        {
            "invoice_id": str(invoice.id),
            "encounter_id": str(invoice.encounter_id),
            "source": "lab",
            "source_id": str(result.id),
        },
    )
    return line_item


@transaction.atomic
def auto_create_invoice_item_from_service(encounter, service_catalog_item: ServiceCatalogItem, actor_id: str = "system") -> InvoiceLineItem:
    ensure_encounter_billable(encounter)
    account = _get_or_create_account(encounter.patient, actor_id=actor_id)
    invoice = _get_or_create_open_invoice(account=account, encounter=encounter, actor_id=actor_id)
    line_item = InvoiceLineItem.objects.create(
        invoice=invoice,
        item_type="service",
        description=service_catalog_item.name,
        service_catalog_item=service_catalog_item,
        quantity=Decimal("1.00"),
        unit_price=service_catalog_item.price,
        total_price=service_catalog_item.price,
        service_code=service_catalog_item.code,
        cpt_code=service_catalog_item.revenue_code,
        provider=str(encounter.doctor_id),
        service_date=timezone.now(),
        source_type="service",
        source_id=str(service_catalog_item.id),
    )
    sync_invoice_totals(invoice, actor_id=actor_id)
    return line_item


@transaction.atomic
def auto_create_invoice_item_from_bed_assignment(assignment: BedAssignment, actor_id: str = "system") -> InvoiceLineItem | None:
    if assignment.status != "completed":
        return None
    service_catalog_item = ServiceCatalogItem.objects.filter(
        requires_bed_assignment=True,
        is_active=True,
    ).order_by("price").first()
    if service_catalog_item is None:
        return None
    account = _get_or_create_account(assignment.patient, actor_id=actor_id)
    invoice = _get_or_create_open_invoice(account=account, encounter=assignment.encounter, actor_id=actor_id)
    if invoice.line_items.filter(source_type="bed", source_id=str(assignment.id), archived_at__isnull=True).exists():
        return None
    duration_days = Decimal("1.00")
    if assignment.end_time and assignment.start_time:
        seconds = max((assignment.end_time - assignment.start_time).total_seconds(), 1)
        duration_days = Decimal(str(round(seconds / 86400, 2)))
    line_item = InvoiceLineItem.objects.create(
        invoice=invoice,
        item_type="room",
        description=f"{service_catalog_item.name} - Bed {assignment.bed.bed_number}",
        service_catalog_item=service_catalog_item,
        quantity=duration_days,
        unit_price=service_catalog_item.price,
        total_price=(service_catalog_item.price * duration_days),
        service_code=service_catalog_item.code,
        cpt_code=service_catalog_item.revenue_code,
        provider=assignment.assigned_by,
        service_date=assignment.start_time,
        source_type="bed",
        source_id=str(assignment.id),
    )
    sync_invoice_totals(invoice, actor_id=actor_id)
    return line_item


def _get_or_create_account(patient, actor_id: str) -> PatientAccount:
    account, _ = PatientAccount.objects.get_or_create(
        patient=patient,
        defaults={
            "account_number": f"ACC-{str(patient.id).split('-')[0].upper()}",
            "status": "active",
            "notes": "",
        },
    )
    account.recompute_balances()
    account.save(update_fields=["total_balance", "total_paid", "updated_at"])
    return account


def _get_or_create_open_invoice(*, account: PatientAccount, encounter, actor_id: str) -> Invoice:
    ensure_encounter_billable(encounter)
    invoice = (
        Invoice.objects.filter(
            account=account,
            encounter=encounter,
            status__in=["draft", "issued", "sent", "viewed", "partially_paid", "overdue"],
            archived_at__isnull=True,
        )
        .order_by("-created_at")
        .first()
    )
    if invoice:
        return invoice
    today = timezone.localdate()
    return Invoice.objects.create(
        account=account,
        encounter=encounter,
        invoice_number=f"INV-{today.strftime('%Y%m%d')}-{str(encounter.id).split('-')[0].upper()}",
        invoice_date=today,
        due_date=today,
        subtotal=Decimal("0.00"),
        tax=Decimal("0.00"),
        discount=Decimal("0.00"),
        total_amount=Decimal("0.00"),
        paid_amount=Decimal("0.00"),
        remaining_balance=Decimal("0.00"),
        status="draft",
        created_by=actor_id,
    )


def ensure_invoice_can_be_finalized(invoice: Invoice) -> None:
    if invoice.encounter_id:
        ensure_encounter_closed_for_final_billing(invoice.encounter)
