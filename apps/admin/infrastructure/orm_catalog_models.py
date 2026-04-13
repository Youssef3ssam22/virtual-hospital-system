"""Catalog models for admin-managed services and exams."""
import uuid
from decimal import Decimal
from django.db import models


class LabCatalogItem(models.Model):
    """Lab test catalog item."""

    SPECIMEN_TYPE_CHOICES = [
        ('blood', 'Blood'),
        ('urine', 'Urine'),
        ('serum', 'Serum'),
        ('plasma', 'Plasma'),
        ('saliva', 'Saliva'),
        ('tissue', 'Tissue'),
        ('stool', 'Stool'),
        ('csf', 'Cerebrospinal Fluid'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        "hospital_administration.Department",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="lab_catalog_items",
    )
    specimen_type = models.CharField(max_length=20, choices=SPECIMEN_TYPE_CHOICES, default='blood')
    sample_container = models.CharField(max_length=100, blank=True, default="")
    minimum_volume_ml = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    default_unit = models.CharField(max_length=50, blank=True)
    fasting_required = models.BooleanField(default=False)
    turnaround_time_minutes = models.PositiveIntegerField(default=60)
    stat_available = models.BooleanField(default=True)
    processing_site = models.CharField(
        max_length=20,
        choices=[('in_house', 'In House'), ('outsource', 'Outsource')],
        default='in_house',
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lab_catalog_items'
        ordering = ['code']

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class RadiologyCatalogItem(models.Model):
    """Radiology exam catalog item."""

    MODALITY_CHOICES = [
        ('xray', 'X-Ray'),
        ('ct', 'CT'),
        ('mri', 'MRI'),
        ('ultrasound', 'Ultrasound'),
        ('nuclear', 'Nuclear Medicine'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        "hospital_administration.Department",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="radiology_catalog_items",
    )
    modality = models.CharField(max_length=20, choices=MODALITY_CHOICES, default='xray')
    body_part = models.CharField(max_length=100, blank=True, default="")
    contrast_required = models.BooleanField(default=False)
    preparation_instructions = models.TextField(blank=True, default="")
    duration_minutes = models.PositiveIntegerField(default=15)
    sedation_required = models.BooleanField(default=False)
    uses_radiation = models.BooleanField(default=True)
    report_turnaround_minutes = models.PositiveIntegerField(default=120)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'radiology_catalog_items'
        ordering = ['code']

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class ServiceCatalogItem(models.Model):
    """General service catalog item."""

    CATEGORY_CHOICES = [
        ('consultation', 'Consultation'),
        ('procedure', 'Procedure'),
        ('room', 'Room/Bed'),
        ('nursing', 'Nursing'),
        ('other', 'Other'),
    ]

    SERVICE_CLASS_CHOICES = [
        ('clinical', 'Clinical'),
        ('diagnostic', 'Diagnostic'),
        ('room_and_board', 'Room And Board'),
        ('administrative', 'Administrative'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        "hospital_administration.Department",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="service_catalog_items",
    )
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='consultation')
    service_class = models.CharField(max_length=30, choices=SERVICE_CLASS_CHOICES, default='clinical')
    revenue_code = models.CharField(max_length=50, blank=True, default="")
    billing_type = models.CharField(
        max_length=20,
        choices=[('fixed', 'Fixed'), ('per_occurrence', 'Per Occurrence'), ('per_day', 'Per Day'), ('package', 'Package')],
        default='fixed',
    )
    insurance_category = models.CharField(max_length=100, blank=True, default="")
    package_eligible = models.BooleanField(default=False)
    requires_physician_order = models.BooleanField(default=False)
    requires_result_entry = models.BooleanField(default=False)
    requires_bed_assignment = models.BooleanField(default=False)
    service_duration_minutes = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'service_catalog_items'
        ordering = ['code']

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"
