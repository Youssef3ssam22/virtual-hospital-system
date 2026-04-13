"""Billing ORM Models - Accounts, Invoices, Insurance, Payments."""
import uuid
from django.db import models
from decimal import Decimal
from django.utils import timezone


class PatientAccount(models.Model):
    """Patient billing account."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('closed', 'Closed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    patient = models.OneToOneField(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="billing_account",
        null=True,
        blank=True,
    )
    account_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    total_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_paid = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    insurance_info = models.JSONField(null=True, blank=True)
    preferred_payment_method = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patient_accounts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Account {self.account_number}"

    def recompute_balances(self):
        invoices_total = self.invoices.exclude(status__in=["void", "cancelled"]).aggregate(
            total=models.Sum("total_amount")
        )["total"] or Decimal("0.00")
        payments_total = self.payments.filter(status="processed").aggregate(
            total=models.Sum("payment_amount")
        )["total"] or Decimal("0.00")
        self.total_paid = payments_total
        self.total_balance = max(Decimal("0.00"), invoices_total - payments_total)
        return self.total_balance


class Invoice(models.Model):
    """Patient invoice model."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('sent', 'Sent'),
        ('viewed', 'Viewed'),
        ('partially_paid', 'Partially Paid'),
        ('fully_paid', 'Fully Paid'),
        ('overdue', 'Overdue'),
        ('void', 'Void'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    account = models.ForeignKey(PatientAccount, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=100, unique=True)
    encounter = models.ForeignKey(
        "patients.Encounter",
        on_delete=models.PROTECT,
        related_name="invoices",
        null=True,
        blank=True,
    )
    invoice_date = models.DateField()
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    tax = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    remaining_balance = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    payment_terms = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.CharField(max_length=255)
    sent_at = models.DateTimeField(blank=True, null=True)
    viewed_at = models.DateTimeField(blank=True, null=True)
    voided_at = models.DateTimeField(blank=True, null=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-invoice_date']
        indexes = [
            models.Index(fields=['account']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"

    def recompute_totals(self):
        subtotal = self.line_items.filter(archived_at__isnull=True).aggregate(
            total=models.Sum("total_price")
        )["total"] or Decimal("0.00")
        self.subtotal = subtotal
        self.total_amount = subtotal + self.tax - self.discount
        self.remaining_balance = max(Decimal("0.00"), self.total_amount - self.paid_amount)
        return self.total_amount


class InvoiceLineItem(models.Model):
    """Line items in invoice."""
    
    ITEM_TYPE_CHOICES = [
        ('service', 'Service'),
        ('medication', 'Medication'),
        ('procedure', 'Procedure'),
        ('room', 'Room/Bed'),
        ('lab', 'Lab Test'),
        ('imaging', 'Imaging'),
        ('other', 'Other'),
    ]

    SOURCE_TYPE_CHOICES = [
        ("lab", "Laboratory"),
        ("radiology", "Radiology"),
        ("service", "Service"),
        ("bed", "Bed Assignment"),
        ("manual", "Manual"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    item_type = models.CharField(max_length=50, choices=ITEM_TYPE_CHOICES)
    description = models.CharField(max_length=500)
    service_catalog_item = models.ForeignKey(
        "hospital_administration.ServiceCatalogItem",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="invoice_line_items",
    )
    lab_catalog_item = models.ForeignKey(
        "hospital_administration.LabCatalogItem",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="invoice_line_items",
    )
    radiology_catalog_item = models.ForeignKey(
        "hospital_administration.RadiologyCatalogItem",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="invoice_line_items",
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)
    service_code = models.CharField(max_length=100, blank=True)
    cpt_code = models.CharField(max_length=50, blank=True)
    icd10_code = models.CharField(max_length=20, blank=True)
    provider = models.CharField(max_length=255, blank=True)
    service_date = models.DateTimeField(default=timezone.now)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES, default="manual")
    source_id = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'invoice_line_items'
        ordering = ['invoice', '-created_at']
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.description}"


class Payment(models.Model):
    """Payment record model."""
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('insurance', 'Insurance'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    account = models.ForeignKey(PatientAccount, on_delete=models.CASCADE, related_name='payments')
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="payments",
        null=True,
        blank=True,
    )
    payment_amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateTimeField()
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, blank=True, unique=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    recorded_by = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    receipt_generated = models.BooleanField(default=False)
    receipt_url = models.URLField(blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['account', 'status']),
            models.Index(fields=['payment_date']),
        ]
    
    def __str__(self):
        return f"Payment {self.reference_number}"


class InsuranceClaim(models.Model):
    """Insurance claim model."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
        ('appealed', 'Appealed'),
        ('resubmitted', 'Resubmitted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE, related_name='insurance_claim')
    claim_number = models.CharField(max_length=100, unique=True)
    insurance_company_id = models.CharField(max_length=255)
    patient_policy_number = models.CharField(max_length=100)
    claim_amount = models.DecimalField(max_digits=15, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    submitted_date = models.DateField(blank=True, null=True)
    approved_date = models.DateField(blank=True, null=True)
    denial_reason = models.TextField(blank=True)
    eob_data = models.JSONField(default=dict, blank=True)
    resubmission_count = models.PositiveIntegerField(default=0)
    last_resubmitted_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'insurance_claims'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Claim {self.claim_number}"


class ClaimDenial(models.Model):
    """Claim denial/rejection record."""
    
    DENIAL_CODE_CHOICES = [
        ('authorization_required', 'Authorization Required'),
        ('not_covered', 'Service Not Covered'),
        ('duplicate_claim', 'Duplicate Claim'),
        ('out_of_network', 'Out of Network'),
        ('provider_not_recognized', 'Provider Not Recognized'),
        ('invalid_code', 'Invalid Service Code'),
        ('missing_documentation', 'Missing Documentation'),
        ('policy_lapsed', 'Policy Lapsed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    claim = models.ForeignKey(InsuranceClaim, on_delete=models.CASCADE, related_name='denials')
    denial_code = models.CharField(max_length=100, choices=DENIAL_CODE_CHOICES)
    denial_reason = models.TextField()
    insurance_message = models.TextField(blank=True)
    appeal_possible = models.BooleanField(default=True)
    days_to_appeal = models.IntegerField(default=30)
    appeal_status = models.CharField(max_length=30, blank=True, default="")
    appealed_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'claim_denials'
    
    def __str__(self):
        return f"Denial {self.denial_code}"


class FinancialTimeline(models.Model):
    """Financial transaction timeline."""
    
    TRANSACTION_TYPE_CHOICES = [
        ('invoice', 'Invoice Issued'),
        ('payment', 'Payment Received'),
        ('adjustment', 'Adjustment'),
        ('refund', 'Refund'),
        ('claim_approval', 'Claim Approved'),
        ('claim_denial', 'Claim Denied'),
        ('collection', 'Collection Action'),
        ('invoice_voided', 'Invoice Voided'),
        ('claim_submitted', 'Claim Submitted'),
        ('claim_paid', 'Claim Paid'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    account = models.ForeignKey(PatientAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES)
    reference_id = models.CharField(max_length=255)  # Invoice/Payment/Claim ID
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=500)
    recorded_by = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'financial_timeline'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"


class Transaction(models.Model):
    """Immutable financial ledger for charges, payments, and adjustments."""

    TYPE_CHOICES = [
        ("charge", "Charge"),
        ("payment", "Payment"),
        ("adjustment", "Adjustment"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    account = models.ForeignKey(PatientAccount, on_delete=models.CASCADE, related_name="ledger_transactions")
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name="ledger_transactions")
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name="ledger_transactions")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    reference_id = models.CharField(max_length=255, db_index=True)
    created_by = models.CharField(max_length=255, blank=True, default="system")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "billing_transactions"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["account", "timestamp"]),
            models.Index(fields=["type", "timestamp"]),
        ]

    def save(self, *args, **kwargs):
        if self.pk and Transaction.objects.filter(pk=self.pk).exists():
            raise ValueError("Financial transactions are immutable and cannot be modified.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Financial transactions are immutable and cannot be deleted.")


class BillingStats(models.Model):
    """Aggregated billing statistics."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    month = models.DateField()  # First day of month
    total_invoices = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_collected = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_outstanding = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    insurance_claims_count = models.IntegerField(default=0)
    insurance_approved = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    average_collection_days = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    collection_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))  # Percentage
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'billing_stats'
        ordering = ['-month']
        unique_together = ('month',)
        verbose_name = 'Billing stats'
        verbose_name_plural = 'Billing stats'
    
    def __str__(self):
        return f"Stats {self.month.strftime('%Y-%m')}"
