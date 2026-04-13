"""Django admin configuration for Billing module."""
from django.contrib import admin
from apps.billing.infrastructure.orm_billing_models import (
    PatientAccount, Invoice, InvoiceLineItem, Payment,
    InsuranceClaim, ClaimDenial, FinancialTimeline, BillingStats, Transaction
)


@admin.register(PatientAccount)
class PatientAccountAdmin(admin.ModelAdmin):
    """Admin interface for PatientAccount."""
    list_display = ('account_number', 'patient', 'status', 'total_balance', 'total_paid')
    list_filter = ('status', 'created_at')
    search_fields = ('patient__mrn', 'patient__full_name', 'account_number')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_per_page = 25
    date_hierarchy = 'created_at'
    list_select_related = ('patient',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin interface for Invoice."""
    list_display = ('invoice_number', 'account', 'total_amount', 'paid_amount', 'status', 'invoice_date')
    list_filter = ('status', 'invoice_date')
    search_fields = ('invoice_number', 'account__patient__mrn', 'account__patient__full_name')
    ordering = ('-invoice_date',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_per_page = 25
    list_select_related = ('account',)
    date_hierarchy = 'invoice_date'


@admin.register(InvoiceLineItem)
class InvoiceLineItemAdmin(admin.ModelAdmin):
    """Admin interface for InvoiceLineItem."""
    list_display = ('invoice', 'description', 'quantity', 'unit_price', 'total_price')
    list_filter = ('item_type', 'created_at')
    search_fields = ('invoice__invoice_number', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')
    list_per_page = 30
    list_select_related = ('invoice',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment."""
    list_display = ('reference_number', 'account', 'payment_amount', 'payment_method', 'status', 'payment_date')
    list_filter = ('status', 'payment_method', 'payment_date')
    search_fields = ('reference_number', 'account__patient__mrn', 'account__patient__full_name')
    ordering = ('-payment_date',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_per_page = 25
    list_select_related = ('account', 'invoice')
    date_hierarchy = 'payment_date'


@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(admin.ModelAdmin):
    """Admin interface for InsuranceClaim."""
    list_display = ('claim_number', 'invoice', 'claim_amount', 'approved_amount', 'status', 'submitted_date')
    list_filter = ('status', 'submitted_date')
    search_fields = ('claim_number', 'invoice__invoice_number')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_per_page = 25
    list_select_related = ('invoice',)


@admin.register(ClaimDenial)
class ClaimDenialAdmin(admin.ModelAdmin):
    """Admin interface for ClaimDenial."""
    list_display = ('claim', 'denial_code', 'appeal_possible', 'days_to_appeal')
    list_filter = ('denial_code', 'appeal_possible')
    search_fields = ('claim__claim_number',)
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')


@admin.register(FinancialTimeline)
class FinancialTimelineAdmin(admin.ModelAdmin):
    """Admin interface for FinancialTimeline."""
    list_display = ('account', 'transaction_type', 'amount', 'balance_after', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('account__patient__mrn', 'account__patient__full_name', 'reference_id')
    ordering = ('-created_at',)
    readonly_fields = fields = ('id', 'created_at')
    list_per_page = 30
    list_select_related = ('account',)


@admin.register(BillingStats)
class BillingStatsAdmin(admin.ModelAdmin):
    """Admin interface for BillingStats."""
    list_display = ('month', 'total_invoices', 'total_amount', 'total_collected', 'collection_rate')
    list_filter = ('month',)
    ordering = ('-month',)
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Immutable financial ledger view."""
    list_display = ('type', 'account', 'invoice', 'payment', 'amount', 'timestamp')
    list_filter = ('type', 'timestamp')
    search_fields = ('reference_id', 'account__account_number', 'account__patient__mrn')
    ordering = ('-timestamp',)
    readonly_fields = ('id', 'account', 'invoice', 'payment', 'type', 'amount', 'timestamp', 'reference_id', 'created_by', 'metadata')
