"""Django ORM models for lab."""

import uuid
from django.db import models
from django.utils import timezone


class LabOrder(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    )

    PRIORITY_CHOICES = (
        ("ROUTINE", "Routine"),
        ("URGENT", "Urgent"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="lab_orders", null=True, blank=True)
    encounter = models.ForeignKey("patients.Encounter", on_delete=models.PROTECT, related_name="lab_orders", null=True, blank=True)
    test_codes = models.JSONField(default=list)
    ordered_by = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="ROUTINE")
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lab_orders"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Lab Order {self.id}"


class Specimen(models.Model):
    """Specimen model for lab samples."""
    
    SPECIMEN_TYPE_CHOICES = [
        ('blood', 'Blood'),
        ('urine', 'Urine'),
        ('serum', 'Serum'),
        ('plasma', 'Plasma'),
        ('saliva', 'Saliva'),
        ('tissue', 'Tissue'),
        ('stool', 'Stool'),
        ('csf', 'Cerebrospinal Fluid'),
    ]
    
    COLLECTION_METHOD_CHOICES = [
        ('venipuncture', 'Venipuncture'),
        ('capillary', 'Capillary'),
        ('clean_catch', 'Clean Catch'),
        ('needle_aspiration', 'Needle Aspiration'),
        ('biopsy', 'Biopsy'),
    ]
    
    STATUS_CHOICES = [
        ('ordered', 'Ordered'),
        ('collected', 'Collected'),
        ('in_transit', 'In Transit'),
        ('received', 'Received'),
        ('processing', 'Processing'),
        ('analyzed', 'Analyzed'),
        ('resulted', 'Resulted'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    ]

    CONDITION_CHOICES = [
        ('acceptable', 'Acceptable'),
        ('hemolyzed', 'Hemolyzed'),
        ('lipemic', 'Lipemic'),
        ('icteric', 'Icteric'),
        ('clotted', 'Clotted'),
        ('insufficient', 'Insufficient'),
        ('wrong_tube', 'Wrong Tube'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    accession_number = models.CharField(max_length=100, unique=True)
    order = models.ForeignKey(LabOrder, on_delete=models.PROTECT, related_name="specimens", null=True, blank=True)
    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="specimens", null=True, blank=True)
    encounter = models.ForeignKey("patients.Encounter", on_delete=models.PROTECT, related_name="specimens", null=True, blank=True)
    specimen_type = models.CharField(max_length=50, choices=SPECIMEN_TYPE_CHOICES)
    collection_method = models.CharField(max_length=50, choices=COLLECTION_METHOD_CHOICES)
    collection_time = models.DateTimeField()
    received_time = models.DateTimeField(null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_unit = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='collected')
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES, blank=True, null=True)
    collector_id = models.CharField(max_length=255, blank=True, null=True)
    rejection_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'specimens'
        ordering = ['-collection_time']


class LabResult(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('verified', 'Verified'),
        ('preliminary', 'Preliminary'),
        ('amended', 'Amended'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(LabOrder, on_delete=models.CASCADE, related_name="results")
    specimen = models.ForeignKey(Specimen, on_delete=models.CASCADE, related_name='results', null=True, blank=True)
    encounter = models.ForeignKey("patients.Encounter", on_delete=models.PROTECT, related_name="lab_results", null=True, blank=True)
    test_code = models.CharField(max_length=50, db_index=True)
    test_name = models.CharField(max_length=255)
    result_value = models.TextField()
    unit = models.CharField(max_length=50, blank=True)
    reference_range = models.CharField(max_length=100, blank=True, null=True)
    reference_range_low = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    reference_range_high = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    abnormal = models.BooleanField(default=False)
    abnormal_flag = models.CharField(
        max_length=5,
        choices=[('N', 'Normal'), ('L', 'Low'), ('H', 'High'), ('LL', 'Critical Low'), ('HH', 'Critical High')],
        default='N'
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    analyzer_id = models.CharField(max_length=255, blank=True)
    reported_by = models.CharField(max_length=255)
    reported_at = models.DateTimeField(auto_now_add=True)
    verified_by = models.CharField(max_length=255, blank=True, null=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    correction_of = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="corrections",
    )
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "lab_results"
        ordering = ["-reported_at"]

    def __str__(self) -> str:
        return f"{self.test_code} - {self.result_value}"


class CriticalValue(models.Model):
    """Critical value alert model."""
    
    PRIORITY_CHOICES = [
        ('high', 'High Priority'),
        ('medium', 'Medium Priority'),
        ('low', 'Low Priority'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('acknowledged', 'Acknowledged'),
        ('acted_upon', 'Acted Upon'),
        ('resolved', 'Resolved'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    result = models.OneToOneField(LabResult, on_delete=models.CASCADE, related_name='critical_value')
    patient_id = models.CharField(max_length=255)
    test_name = models.CharField(max_length=255)
    critical_value = models.CharField(max_length=500)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='high')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new')
    reported_to = models.CharField(max_length=255, blank=True, null=True)
    reported_at = models.DateTimeField(blank=True, null=True)
    acknowledged_by = models.CharField(max_length=255, blank=True, null=True)
    acknowledged_at = models.DateTimeField(blank=True, null=True)
    action_taken = models.TextField(blank=True)
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'critical_values'
        ordering = ['-created_at']


class LabReport(models.Model):
    """Lab report model - aggregates results for an order."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('preliminary', 'Preliminary'),
        ('final', 'Final'),
        ('corrected', 'Corrected'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    order = models.OneToOneField(LabOrder, on_delete=models.PROTECT, related_name="report", null=True, blank=True)
    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="lab_reports", null=True, blank=True)
    encounter = models.ForeignKey("patients.Encounter", on_delete=models.PROTECT, related_name="lab_reports", null=True, blank=True)
    specimen = models.ForeignKey(Specimen, on_delete=models.PROTECT, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    report_number = models.CharField(max_length=100, unique=True)
    generated_at = models.DateTimeField()
    completed_at = models.DateTimeField(blank=True, null=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    generated_by = models.CharField(max_length=255)
    verified_by = models.CharField(max_length=255, blank=True, null=True)
    interpretation = models.TextField(blank=True)
    critical_values_count = models.IntegerField(default=0)
    attachments = models.JSONField(default=list)
    released_at = models.DateTimeField(blank=True, null=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lab_reports'
        ordering = ['-generated_at']


class RecollectionRequest(models.Model):
    """Request to recollect a specimen."""

    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('collected', 'Collected'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    specimen = models.ForeignKey(Specimen, on_delete=models.CASCADE, related_name='recollection_requests')
    reason = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'specimen_recollection_requests'
        ordering = ['-requested_at']


class AnalyzerQueue(models.Model):
    """Analyzer queue for managing specimen processing."""
    
    PRIORITY_CHOICES = [
        ('routine', 'Routine'),
        ('stat', 'STAT'),
        ('priority', 'Priority'),
    ]
    
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('retry', 'Retry'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    specimen = models.ForeignKey(Specimen, on_delete=models.CASCADE)
    analyzer_id = models.CharField(max_length=255)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default='routine')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='queued')
    position_in_queue = models.IntegerField()
    queued_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analyzer_queue'
        ordering = ['priority', 'position_in_queue']

    def mark_processing(self):
        self.status = "processing"
        self.started_at = timezone.now()

    def mark_completed(self):
        self.status = "completed"
        self.completed_at = timezone.now()

