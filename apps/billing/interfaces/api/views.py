"""Billing API views for Accounts, Invoices, Payments, Claims."""
from datetime import date, datetime
from decimal import Decimal

from django.db import transaction
from django.db.models import Avg, Count, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.billing.infrastructure.orm_billing_models import (
    BillingStats,
    ClaimDenial,
    FinancialTimeline,
    InsuranceClaim,
    Invoice,
    InvoiceLineItem,
    PatientAccount,
    Payment,
)
from apps.billing.interfaces.serializers import (
    BillingStatsSerializer,
    ClaimDenialSerializer,
    FinancialTimelineSerializer,
    InsuranceClaimSerializer,
    InvoiceLineItemSerializer,
    InvoiceSerializer,
    PatientAccountSerializer,
    PaymentSerializer,
)
from apps.billing.services import (
    apply_payment,
    assert_claim_transition,
    assert_invoice_transition,
    auto_create_invoice_item_from_service,
    ensure_invoice_can_be_finalized,
    record_adjustment,
    sync_invoice_totals,
)
from infrastructure.audit.audit_logger import AuditLogger
from shared.permissions import CanManageBilling
from shared.utils.notifications import emit_event


def _actor_id(request) -> str:
    return str(request.user.id) if hasattr(request.user, "id") else "system"


def _actor_role(request) -> str:
    return getattr(request.user, "role", "UNKNOWN")


def _audit_billing_action(request, action: str, entity_type: str, entity_id: str, detail: dict):
    AuditLogger().log(
        actor_id=_actor_id(request),
        actor_role=_actor_role(request),
        action=action,
        source_module="billing",
        entity_type=entity_type,
        entity_id=entity_id,
        detail=detail,
        outcome="success",
    )


class PatientAccountViewSet(viewsets.ModelViewSet):
    queryset = PatientAccount.objects.select_related("patient")
    serializer_class = PatientAccountSerializer
    permission_classes = [CanManageBilling]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status"]
    search_fields = ["patient__mrn", "patient__full_name", "account_number"]
    ordering_fields = ["total_balance", "created_at"]
    ordering = ["-created_at"]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "billing"

    def get_queryset(self):
        queryset = super().get_queryset().filter(archived_at__isnull=True)
        for account in queryset:
            account.recompute_balances()
        return queryset

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        account = self.get_object()
        account.recompute_balances()
        invoices = account.invoices.filter(archived_at__isnull=True)
        payments = account.payments.filter(status="processed", archived_at__isnull=True)
        claims = InsuranceClaim.objects.filter(invoice__account=account, archived_at__isnull=True)
        return Response(
            {
                "account": PatientAccountSerializer(account).data,
                "summary": {
                    "total_invoices": invoices.count(),
                    "total_amount": str(invoices.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")),
                    "paid_amount": str(payments.aggregate(total=Sum("payment_amount"))["total"] or Decimal("0.00")),
                    "outstanding": str(account.total_balance),
                    "insurance_claims": claims.count(),
                    "approved_claims": str(claims.aggregate(total=Sum("approved_amount"))["total"] or Decimal("0.00")),
                },
                "recent_transactions": FinancialTimelineSerializer(account.transactions.all()[:10], many=True).data,
            }
        )

    def perform_destroy(self, instance):
        instance.archived_at = datetime.utcnow()
        instance.status = "closed"
        instance.save(update_fields=["archived_at", "status", "updated_at"])


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related("account", "encounter", "account__patient")
    serializer_class = InvoiceSerializer
    permission_classes = [CanManageBilling]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "account", "encounter"]
    search_fields = ["invoice_number", "account__patient__mrn", "account__patient__full_name"]
    ordering_fields = ["invoice_date", "due_date", "total_amount"]
    ordering = ["-invoice_date"]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "billing"

    def get_queryset(self):
        return super().get_queryset().filter(archived_at__isnull=True)

    @transaction.atomic
    def perform_create(self, serializer):
        invoice = serializer.save()
        sync_invoice_totals(invoice, actor_id=_actor_id(self.request))
        _audit_billing_action(self.request, "BILLING_INVOICE_CREATED", "Invoice", str(invoice.id), {"status": invoice.status})

    @transaction.atomic
    def perform_update(self, serializer):
        invoice = serializer.save()
        sync_invoice_totals(invoice, actor_id=_actor_id(self.request))

    def perform_destroy(self, instance):
        if instance.paid_amount > 0:
            raise ValueError("Paid invoices cannot be deleted; void them instead.")
        instance.archived_at = datetime.utcnow()
        instance.status = "cancelled"
        instance.save(update_fields=["archived_at", "status", "updated_at"])

    @action(detail=True, methods=["post"])
    def add_line_item(self, request, pk=None):
        invoice = self.get_object()
        serializer = InvoiceLineItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        line_item = serializer.save(invoice=invoice)
        sync_invoice_totals(invoice, actor_id=_actor_id(request))
        return Response(InvoiceLineItemSerializer(line_item).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        invoice = self.get_object()
        ensure_invoice_can_be_finalized(invoice)
        assert_invoice_transition(invoice, "sent")
        invoice.status = "sent"
        invoice.sent_at = datetime.utcnow()
        invoice.save(update_fields=["status", "sent_at", "updated_at"])
        emit_event("billing", "invoice_created", {"invoice_id": str(invoice.id), "patient_id": str(invoice.account.patient_id)})
        return Response(InvoiceSerializer(invoice).data)

    @action(detail=True, methods=["post"])
    def void(self, request, pk=None):
        invoice = self.get_object()
        assert_invoice_transition(invoice, "void")
        if invoice.paid_amount > 0:
            return Response({"detail": "Cannot void invoice with processed payments."}, status=status.HTTP_400_BAD_REQUEST)
        invoice.status = "void"
        invoice.voided_at = datetime.utcnow()
        invoice.save(update_fields=["status", "voided_at", "updated_at"])
        invoice.account.recompute_balances()
        invoice.account.save(update_fields=["total_balance", "total_paid", "updated_at"])
        record_adjustment(
            account=invoice.account,
            invoice=invoice,
            amount=invoice.total_amount,
            reference_id=str(invoice.id),
            actor_id=_actor_id(request),
            metadata={"reason": "invoice_void"},
        )
        FinancialTimeline.objects.create(
            account=invoice.account,
            transaction_type="invoice_voided",
            reference_id=str(invoice.id),
            amount=invoice.total_amount,
            balance_after=invoice.account.total_balance,
            description=f"Invoice {invoice.invoice_number} voided",
            recorded_by=_actor_id(request),
            metadata={"invoice_number": invoice.invoice_number},
        )
        return Response(InvoiceSerializer(invoice).data)

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        today = date.today()
        invoices = self.get_queryset().filter(due_date__lt=today, status__in=["issued", "sent", "viewed", "partially_paid"])
        return Response(self.get_serializer(invoices, many=True).data)

    @action(detail=False, methods=["post"])
    def add_service_item(self, request):
        encounter_id = request.data.get("encounter")
        service_catalog_item_id = request.data.get("service_catalog_item")
        if not encounter_id or not service_catalog_item_id:
            return Response({"detail": "encounter and service_catalog_item are required."}, status=status.HTTP_400_BAD_REQUEST)
        from apps.admin.infrastructure.orm_catalog_models import ServiceCatalogItem
        from apps.patients.infrastructure.orm_models import Encounter

        encounter = Encounter.objects.get(id=encounter_id)
        service_catalog_item = ServiceCatalogItem.objects.get(id=service_catalog_item_id)
        line_item = auto_create_invoice_item_from_service(encounter, service_catalog_item, actor_id=_actor_id(request))
        return Response(InvoiceLineItemSerializer(line_item).data, status=status.HTTP_201_CREATED)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("account", "invoice", "patient")
    serializer_class = PaymentSerializer
    permission_classes = [CanManageBilling]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "payment_method", "account", "patient"]
    search_fields = ["reference_number", "account__patient__mrn", "account__patient__full_name"]
    ordering_fields = ["payment_date", "payment_amount"]
    ordering = ["-payment_date"]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "billing"

    def get_queryset(self):
        return super().get_queryset().filter(archived_at__isnull=True)

    @action(detail=True, methods=["post"])
    def process(self, request, pk=None):
        payment = apply_payment(self.get_object(), actor_id=_actor_id(request))
        _audit_billing_action(request, "BILLING_PAYMENT_PROCESSED", "Payment", str(payment.id), {"amount": str(payment.payment_amount)})
        return Response(PaymentSerializer(payment).data)

    @action(detail=True, methods=["post"])
    def void(self, request, pk=None):
        payment = self.get_object()
        if payment.status == "processed":
            return Response({"detail": "Processed payments should be refunded, not voided."}, status=status.HTTP_400_BAD_REQUEST)
        payment.status = "cancelled"
        payment.notes = request.data.get("reason", payment.notes)
        payment.save(update_fields=["status", "notes", "updated_at"])
        return Response(PaymentSerializer(payment).data)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        payments = self.get_queryset().filter(status="processed")
        return Response(
            {
                "total_payments": payments.count(),
                "total_amount": str(payments.aggregate(total=Sum("payment_amount"))["total"] or Decimal("0.00")),
                "by_method": list(
                    payments.values("payment_method").annotate(count=Count("id"), total=Sum("payment_amount"))
                ),
            }
        )


class InsuranceClaimViewSet(viewsets.ModelViewSet):
    queryset = InsuranceClaim.objects.select_related("invoice", "invoice__account")
    serializer_class = InsuranceClaimSerializer
    permission_classes = [CanManageBilling]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "insurance_company_id"]
    ordering_fields = ["submitted_date", "approved_date"]
    ordering = ["-created_at"]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "billing"

    def get_queryset(self):
        return super().get_queryset().filter(archived_at__isnull=True)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def submit(self, request, pk=None):
        claim = InsuranceClaim.objects.select_for_update().select_related("invoice", "invoice__account").get(pk=self.get_object().pk)
        assert_claim_transition(claim, "submitted")
        claim.status = "submitted"
        claim.submitted_date = date.today()
        claim.save(update_fields=["status", "submitted_date", "updated_at"])
        FinancialTimeline.objects.create(
            account=claim.invoice.account,
            transaction_type="claim_submitted",
            reference_id=str(claim.id),
            amount=claim.claim_amount,
            balance_after=claim.invoice.account.total_balance,
            description=f"Claim {claim.claim_number} submitted",
            recorded_by=_actor_id(request),
        )
        return Response(InsuranceClaimSerializer(claim).data)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def approve(self, request, pk=None):
        claim = InsuranceClaim.objects.select_for_update().select_related("invoice", "invoice__account").get(pk=self.get_object().pk)
        assert_claim_transition(claim, "approved")
        approved_amount = Decimal(str(request.data.get("approved_amount", claim.claim_amount)))
        claim.status = "approved"
        claim.approved_amount = approved_amount
        claim.approved_date = date.today()
        claim.eob_data = request.data.get("eob_data", claim.eob_data)
        claim.save(update_fields=["status", "approved_amount", "approved_date", "eob_data", "updated_at"])
        return Response(InsuranceClaimSerializer(claim).data)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def reject(self, request, pk=None):
        claim = InsuranceClaim.objects.select_for_update().select_related("invoice", "invoice__account").get(pk=self.get_object().pk)
        assert_claim_transition(claim, "rejected")
        claim.status = "rejected"
        claim.denial_reason = request.data.get("denial_reason", "")
        claim.save(update_fields=["status", "denial_reason", "updated_at"])
        denial = ClaimDenial.objects.create(
            claim=claim,
            denial_code=request.data.get("denial_code", "missing_documentation"),
            denial_reason=claim.denial_reason or "Rejected by payer",
            insurance_message=request.data.get("insurance_message", ""),
        )
        return Response({"claim": InsuranceClaimSerializer(claim).data, "denial": ClaimDenialSerializer(denial).data})

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def paid(self, request, pk=None):
        claim = InsuranceClaim.objects.select_for_update().select_related("invoice", "invoice__account").get(pk=self.get_object().pk)
        assert_claim_transition(claim, "paid")
        paid_amount = Decimal(str(request.data.get("paid_amount", claim.approved_amount)))
        claim.status = "paid"
        claim.paid_amount = paid_amount
        claim.save(update_fields=["status", "paid_amount", "updated_at"])
        FinancialTimeline.objects.create(
            account=claim.invoice.account,
            transaction_type="claim_paid",
            reference_id=str(claim.id),
            amount=paid_amount,
            balance_after=claim.invoice.account.total_balance,
            description=f"Claim {claim.claim_number} paid",
            recorded_by=_actor_id(request),
        )
        return Response(InsuranceClaimSerializer(claim).data)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def resubmit(self, request, pk=None):
        claim = InsuranceClaim.objects.select_for_update().select_related("invoice", "invoice__account").get(pk=self.get_object().pk)
        assert_claim_transition(claim, "resubmitted")
        claim.status = "resubmitted"
        claim.resubmission_count += 1
        claim.last_resubmitted_at = datetime.utcnow()
        claim.save(update_fields=["status", "resubmission_count", "last_resubmitted_at", "updated_at"])
        return Response(InsuranceClaimSerializer(claim).data)


class FinancialTimelineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinancialTimeline.objects.select_related("account")
    serializer_class = FinancialTimelineSerializer
    permission_classes = [CanManageBilling]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["account", "transaction_type"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "billing"


class BillingStatsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BillingStats.objects.all()
    serializer_class = BillingStatsSerializer
    permission_classes = [CanManageBilling]
    filter_backends = [OrderingFilter]
    ordering_fields = ["month"]
    ordering = ["-month"]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "billing"

    def list(self, request, *args, **kwargs):
        month = request.query_params.get("month")
        queryset = self._dynamic_stats(month)
        return Response(queryset)

    def _dynamic_stats(self, month: str | None):
        queryset = Invoice.objects.filter(archived_at__isnull=True)
        if month:
            month_date = datetime.fromisoformat(month).date().replace(day=1)
        else:
            today = date.today()
            month_date = today.replace(day=1)
        monthly_invoices = queryset.filter(invoice_date__year=month_date.year, invoice_date__month=month_date.month)
        monthly_payments = Payment.objects.filter(status="processed", payment_date__year=month_date.year, payment_date__month=month_date.month)
        monthly_claims = InsuranceClaim.objects.filter(created_at__year=month_date.year, created_at__month=month_date.month)
        return [{
            "month": month_date,
            "total_invoices": monthly_invoices.count(),
            "total_amount": monthly_invoices.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00"),
            "total_collected": monthly_payments.aggregate(total=Sum("payment_amount"))["total"] or Decimal("0.00"),
            "total_outstanding": monthly_invoices.aggregate(total=Sum("remaining_balance"))["total"] or Decimal("0.00"),
            "insurance_claims_count": monthly_claims.count(),
            "insurance_approved": monthly_claims.aggregate(total=Sum("approved_amount"))["total"] or Decimal("0.00"),
            "average_collection_days": monthly_invoices.exclude(paid_amount=0).aggregate(avg=Avg("due_date"))["avg"] or 0,
            "collection_rate": Decimal("0.00") if monthly_invoices.count() == 0 else round(((monthly_payments.aggregate(total=Sum("payment_amount"))["total"] or Decimal("0.00")) / (monthly_invoices.aggregate(total=Sum("total_amount"))["total"] or Decimal("1.00"))) * 100, 2),
        }]


class ClaimDenialViewSet(viewsets.ModelViewSet):
    queryset = ClaimDenial.objects.select_related("claim")
    serializer_class = ClaimDenialSerializer
    permission_classes = [CanManageBilling]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["denial_code", "appeal_possible", "appeal_status"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "billing"

    @action(detail=True, methods=["post"])
    def appeal(self, request, pk=None):
        denial = self.get_object()
        denial.appeal_status = "submitted"
        denial.appealed_at = datetime.utcnow()
        denial.resolution_notes = request.data.get("appeal_notes", denial.resolution_notes)
        denial.save(update_fields=["appeal_status", "appealed_at", "resolution_notes"])
        return Response(ClaimDenialSerializer(denial).data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        denial = self.get_object()
        denial.appeal_status = "resolved"
        denial.resolved_at = datetime.utcnow()
        denial.resolution_notes = request.data.get("resolution_notes", denial.resolution_notes)
        denial.save(update_fields=["appeal_status", "resolved_at", "resolution_notes"])
        return Response(ClaimDenialSerializer(denial).data)


class AccountByPatientView(APIView):
    permission_classes = [CanManageBilling]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "billing"

    def get(self, request, patient_id: str):
        try:
            account = PatientAccount.objects.select_related("patient").get(patient_id=patient_id, archived_at__isnull=True)
        except PatientAccount.DoesNotExist:
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)
        account.recompute_balances()
        return Response(PatientAccountSerializer(account).data)


class AccountTimelineView(APIView):
    permission_classes = [CanManageBilling]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "billing"

    def get(self, request, patient_id: str):
        try:
            account = PatientAccount.objects.get(patient_id=patient_id, archived_at__isnull=True)
        except PatientAccount.DoesNotExist:
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)
        transactions = FinancialTimeline.objects.filter(account=account).order_by("-created_at")
        return Response(FinancialTimelineSerializer(transactions, many=True).data)
