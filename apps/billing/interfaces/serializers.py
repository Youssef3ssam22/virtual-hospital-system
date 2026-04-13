"""Billing serializers for Accounts, Invoices, Payments, Claims."""
from datetime import timedelta
from decimal import Decimal

from rest_framework import serializers

from apps.admin.infrastructure.orm_admin_extended import SystemSettings
from apps.admin.infrastructure.orm_catalog_models import LabCatalogItem, RadiologyCatalogItem, ServiceCatalogItem
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
from apps.billing.services import assert_claim_transition, assert_invoice_transition
from shared.constants.roles import Role
from shared.utils.encounters import ensure_encounter_billable
from shared.utils.field_filtering import RoleBasedFieldFilterMixin


class PatientAccountSerializer(RoleBasedFieldFilterMixin, serializers.ModelSerializer):
    patient_id = serializers.UUIDField(source="patient_id", read_only=True)
    computed_balance = serializers.SerializerMethodField()
    role_field_permissions = {
        "insurance_info": {Role.ADMIN},
        "notes": {Role.ADMIN},
    }

    class Meta:
        model = PatientAccount
        fields = [
            "id",
            "patient",
            "patient_id",
            "account_number",
            "status",
            "total_balance",
            "total_paid",
            "computed_balance",
            "insurance_info",
            "preferred_payment_method",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_balance", "total_paid", "computed_balance", "created_at", "updated_at"]

    def get_computed_balance(self, obj):
        obj.recompute_balances()
        return obj.total_balance


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLineItem
        fields = [
            "id",
            "invoice",
            "item_type",
            "description",
            "service_catalog_item",
            "lab_catalog_item",
            "radiology_catalog_item",
            "quantity",
            "unit_price",
            "total_price",
            "service_code",
            "cpt_code",
            "icd10_code",
            "provider",
            "service_date",
            "source_type",
            "source_id",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "total_price"]

    def validate(self, data):
        quantity = Decimal(str(data.get("quantity", getattr(self.instance, "quantity", 0) or 0)))
        unit_price = Decimal(str(data.get("unit_price", getattr(self.instance, "unit_price", 0) or 0)))
        selected_catalogs = [
            data.get("service_catalog_item", getattr(self.instance, "service_catalog_item", None)),
            data.get("lab_catalog_item", getattr(self.instance, "lab_catalog_item", None)),
            data.get("radiology_catalog_item", getattr(self.instance, "radiology_catalog_item", None)),
        ]
        selected_catalogs = [item for item in selected_catalogs if item is not None]

        if quantity <= 0:
            raise serializers.ValidationError("quantity must be greater than 0.")
        if unit_price < 0:
            raise serializers.ValidationError("unit_price cannot be negative.")
        if len(selected_catalogs) > 1:
            raise serializers.ValidationError("Line item may only reference one catalog object.")
        if not data.get("description") and not selected_catalogs:
            raise serializers.ValidationError("description is required when no catalog item is linked.")
        for required_field in ("cpt_code", "provider", "service_date", "source_type", "source_id"):
            if not data.get(required_field):
                raise serializers.ValidationError(f"{required_field} is required.")

        catalog_item = selected_catalogs[0] if selected_catalogs else self._resolve_catalog_from_code(
            data.get("service_code", getattr(self.instance, "service_code", ""))
        )
        if catalog_item is not None:
            data.setdefault("description", catalog_item.name)
            data.setdefault("service_code", catalog_item.code)
            data["unit_price"] = Decimal(str(data.get("unit_price") or catalog_item.price))
            if isinstance(catalog_item, ServiceCatalogItem):
                data.setdefault("item_type", "room" if catalog_item.category == "room" else "service")
            elif isinstance(catalog_item, LabCatalogItem):
                data.setdefault("item_type", "lab")
            elif isinstance(catalog_item, RadiologyCatalogItem):
                data.setdefault("item_type", "imaging")
        data["total_price"] = quantity * Decimal(str(data.get("unit_price", unit_price)))
        return data

    @staticmethod
    def _resolve_catalog_from_code(service_code: str):
        if not service_code:
            return None
        code = service_code.strip().upper()
        return (
            ServiceCatalogItem.objects.filter(code__iexact=code, is_active=True).first()
            or LabCatalogItem.objects.filter(code__iexact=code, is_active=True).first()
            or RadiologyCatalogItem.objects.filter(code__iexact=code, is_active=True).first()
        )


class InvoiceSerializer(RoleBasedFieldFilterMixin, serializers.ModelSerializer):
    line_items = InvoiceLineItemSerializer(many=True, read_only=True)
    account_number = serializers.CharField(source="account.account_number", read_only=True)
    encounter_id = serializers.UUIDField(source="encounter_id", read_only=True)
    charge_items = InvoiceLineItemSerializer(many=True, write_only=True, required=False)
    role_field_permissions = {
        "created_by": {Role.ADMIN},
    }

    class Meta:
        model = Invoice
        fields = [
            "id",
            "account",
            "account_number",
            "encounter",
            "encounter_id",
            "invoice_number",
            "invoice_date",
            "due_date",
            "subtotal",
            "tax",
            "discount",
            "total_amount",
            "paid_amount",
            "remaining_balance",
            "status",
            "payment_terms",
            "notes",
            "line_items",
            "charge_items",
            "created_by",
            "sent_at",
            "viewed_at",
            "voided_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "subtotal",
            "total_amount",
            "paid_amount",
            "remaining_balance",
            "sent_at",
            "viewed_at",
            "voided_at",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        invoice_date = data.get("invoice_date", getattr(self.instance, "invoice_date", None))
        due_date = data.get("due_date", getattr(self.instance, "due_date", None))
        tax = Decimal(str(data.get("tax", getattr(self.instance, "tax", 0) or 0)))
        discount = Decimal(str(data.get("discount", getattr(self.instance, "discount", 0) or 0)))
        encounter = data.get("encounter", getattr(self.instance, "encounter", None))
        if tax < 0 or discount < 0:
            raise serializers.ValidationError("tax and discount must be non-negative.")
        if encounter is not None:
            try:
                ensure_encounter_billable(encounter)
            except ValueError as exc:
                raise serializers.ValidationError(str(exc)) from exc
        if invoice_date and not due_date:
            default_days = int(SystemSettings.get_typed_value("BILLING_DEFAULT_DUE_DAYS", 30))
            data["due_date"] = invoice_date + timedelta(days=default_days)
            due_date = data["due_date"]
        if invoice_date and due_date and due_date < invoice_date:
            raise serializers.ValidationError("due_date cannot be earlier than invoice_date.")
        if self.instance and "status" in data:
            assert_invoice_transition(self.instance, data["status"])
        return data

    def create(self, validated_data):
        charge_items = validated_data.pop("charge_items", [])
        validated_data["subtotal"] = Decimal("0.00")
        validated_data["total_amount"] = Decimal("0.00")
        validated_data["paid_amount"] = Decimal("0.00")
        validated_data["remaining_balance"] = Decimal("0.00")
        invoice = super().create(validated_data)
        for item in charge_items:
            serializer = InvoiceLineItemSerializer(data=item)
            serializer.is_valid(raise_exception=True)
            serializer.save(invoice=invoice)
        invoice.recompute_totals()
        invoice.save(update_fields=["subtotal", "total_amount", "remaining_balance", "updated_at"])
        return invoice

    def update(self, instance, validated_data):
        validated_data.pop("charge_items", None)
        invoice = super().update(instance, validated_data)
        invoice.recompute_totals()
        invoice.save(update_fields=["subtotal", "total_amount", "remaining_balance", "updated_at"])
        return invoice


class PaymentSerializer(RoleBasedFieldFilterMixin, serializers.ModelSerializer):
    invoice_number = serializers.CharField(source="invoice.invoice_number", read_only=True, allow_null=True)
    patient_id = serializers.UUIDField(source="patient_id", read_only=True)
    role_field_permissions = {
        "recorded_by": {Role.ADMIN},
        "receipt_url": {Role.ADMIN},
    }

    class Meta:
        model = Payment
        fields = [
            "id",
            "account",
            "invoice",
            "patient",
            "patient_id",
            "invoice_number",
            "payment_amount",
            "payment_date",
            "payment_method",
            "reference_number",
            "status",
            "recorded_by",
            "notes",
            "receipt_generated",
            "receipt_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "receipt_url", "created_at", "updated_at"]

    def validate(self, data):
        payment_amount = Decimal(str(data.get("payment_amount", 0)))
        invoice = data.get("invoice")
        patient = data.get("patient")
        account = data.get("account")
        if payment_amount <= 0:
            raise serializers.ValidationError("payment_amount must be greater than 0.")
        if patient and account and account.patient_id != patient.id:
            raise serializers.ValidationError("Payment patient must match account patient.")
        if invoice and account and invoice.account_id != account.id:
            raise serializers.ValidationError("Invoice must belong to the selected account.")
        allow_overpayment = SystemSettings.get_typed_value("BILLING_ALLOW_OVERPAYMENT", False)
        if invoice and payment_amount > invoice.remaining_balance and not allow_overpayment:
            raise serializers.ValidationError("payment_amount cannot exceed invoice remaining balance.")
        return data


class InsuranceClaimSerializer(RoleBasedFieldFilterMixin, serializers.ModelSerializer):
    invoice_number = serializers.CharField(source="invoice.invoice_number", read_only=True)
    role_field_permissions = {
        "eob_data": {Role.ADMIN},
        "notes": {Role.ADMIN},
    }

    class Meta:
        model = InsuranceClaim
        fields = [
            "id",
            "invoice",
            "invoice_number",
            "claim_number",
            "insurance_company_id",
            "patient_policy_number",
            "claim_amount",
            "approved_amount",
            "paid_amount",
            "status",
            "submitted_date",
            "approved_date",
            "denial_reason",
            "eob_data",
            "resubmission_count",
            "last_resubmitted_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "resubmission_count", "last_resubmitted_at", "created_at", "updated_at"]

    def validate(self, data):
        claim_amount = Decimal(str(data.get("claim_amount", getattr(self.instance, "claim_amount", 0) or 0)))
        approved_amount = Decimal(str(data.get("approved_amount", getattr(self.instance, "approved_amount", 0) or 0)))
        paid_amount = Decimal(str(data.get("paid_amount", getattr(self.instance, "paid_amount", 0) or 0)))
        if approved_amount > claim_amount:
            raise serializers.ValidationError("approved_amount cannot exceed claim_amount.")
        if paid_amount > approved_amount:
            raise serializers.ValidationError("paid_amount cannot exceed approved_amount.")
        if self.instance and "status" in data:
            assert_claim_transition(self.instance, data["status"])
        return data


class ClaimDenialSerializer(RoleBasedFieldFilterMixin, serializers.ModelSerializer):
    role_field_permissions = {
        "resolution_notes": {Role.ADMIN},
    }

    class Meta:
        model = ClaimDenial
        fields = [
            "id",
            "claim",
            "denial_code",
            "denial_reason",
            "insurance_message",
            "appeal_possible",
            "days_to_appeal",
            "appeal_status",
            "appealed_at",
            "resolved_at",
            "resolution_notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class FinancialTimelineSerializer(RoleBasedFieldFilterMixin, serializers.ModelSerializer):
    role_field_permissions = {
        "recorded_by": {Role.ADMIN},
        "metadata": {Role.ADMIN},
    }

    class Meta:
        model = FinancialTimeline
        fields = [
            "id",
            "account",
            "transaction_type",
            "reference_id",
            "amount",
            "balance_after",
            "description",
            "recorded_by",
            "metadata",
            "created_at",
        ]
        read_only_fields = fields


class BillingStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingStats
        fields = [
            "id",
            "month",
            "total_invoices",
            "total_amount",
            "total_collected",
            "total_outstanding",
            "insurance_claims_count",
            "insurance_approved",
            "average_collection_days",
            "collection_rate",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
