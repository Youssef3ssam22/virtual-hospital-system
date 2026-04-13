"""Admin ORM Models - Departments, Wards, Beds."""
import uuid
import re
from django.db import models
from django.utils import timezone


class Department(models.Model):
    """Department model."""

    DEPARTMENT_TYPE_CHOICES = [
        ("inpatient", "Inpatient"),
        ("outpatient", "Outpatient"),
        ("radiology", "Radiology"),
        ("nursery", "Nursery"),
        ("laboratory", "Laboratory"),
        ("pharmacy", "Pharmacy"),
        ("billing", "Billing"),
        ("administration", "Administration"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True)
    department_type = models.CharField(max_length=30, choices=DEPARTMENT_TYPE_CHOICES, default="administration")
    description = models.TextField(blank=True)
    head_id = models.CharField(max_length=255, blank=True, null=True)  # References User
    manager_name = models.CharField(max_length=255, blank=True, default="")
    location = models.CharField(max_length=255, blank=True, default="")
    floor = models.CharField(max_length=50, blank=True, default="")
    extension_phone = models.CharField(max_length=20, blank=True, default="")
    operating_hours = models.CharField(max_length=100, blank=True, default="24/7")
    is_clinical = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departments'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Ward(models.Model):
    """Ward model."""

    WARD_TYPE_CHOICES = [
        ("general", "General Ward"),
        ("icu", "ICU"),
        ("pediatric", "Pediatric"),
        ("maternity", "Maternity"),
        ("nursery", "Nursery"),
        ("observation", "Observation"),
        ("isolation", "Isolation"),
    ]

    GENDER_RESTRICTION_CHOICES = [
        ("mixed", "Mixed"),
        ("male", "Male"),
        ("female", "Female"),
    ]

    AGE_GROUP_CHOICES = [
        ("mixed", "Mixed"),
        ("adult", "Adult"),
        ("pediatric", "Pediatric"),
        ("neonatal", "Neonatal"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("maintenance", "Maintenance"),
        ("closed", "Closed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    type = models.CharField(max_length=50, choices=WARD_TYPE_CHOICES)
    gender_restriction = models.CharField(max_length=10, choices=GENDER_RESTRICTION_CHOICES, default="mixed")
    age_group = models.CharField(max_length=20, choices=AGE_GROUP_CHOICES, default="mixed")
    specialty = models.CharField(max_length=100, blank=True, default="")
    nurse_station = models.CharField(max_length=100, blank=True, default="")
    supports_isolation = models.BooleanField(default=False)
    total_beds = models.IntegerField()
    available_beds = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wards'
        ordering = ['name']
        unique_together = ('department', 'code')

    def __str__(self):
        return f"{self.name} - {self.department.name}"


class Bed(models.Model):
    """Bed model."""

    BED_TYPE_CHOICES = [
        ("standard", "Standard"),
        ("private", "Private"),
        ("icu", "ICU"),
        ("pediatric", "Pediatric"),
        ("incubator", "Incubator"),
    ]

    BED_CLASS_CHOICES = [
        ("general", "General"),
        ("private", "Private"),
        ("isolation", "Isolation"),
        ("critical_care", "Critical Care"),
        ("newborn", "Newborn"),
    ]

    STATUS_CHOICES = [
        ("available", "Available"),
        ("occupied", "Occupied"),
        ("reserved", "Reserved"),
        ("maintenance", "Maintenance"),
        ("cleaning", "Cleaning"),
        ("blocked", "Blocked"),
    ]

    CLEANING_STATUS_CHOICES = [
        ("clean", "Clean"),
        ("needs_cleaning", "Needs Cleaning"),
        ("cleaning_in_progress", "Cleaning In Progress"),
        ("sanitized", "Sanitized"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    room_number = models.CharField(max_length=50, blank=True, default="")
    bed_number = models.CharField(max_length=50, blank=True)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='beds')
    type = models.CharField(max_length=50, choices=BED_TYPE_CHOICES)
    bed_class = models.CharField(max_length=30, choices=BED_CLASS_CHOICES, default="general")
    features = models.JSONField(default=list)  # ['oxygen', 'monitor', 'ventilator']
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    cleaning_status = models.CharField(
        max_length=30,
        choices=CLEANING_STATUS_CHOICES,
        default="clean",
    )
    blocked_reason = models.TextField(blank=True, default="")
    patient_id = models.CharField(max_length=255, blank=True, null=True)
    occupied_since = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'beds'
        ordering = ['bed_number']
        unique_together = ('ward', 'bed_number')

    def __str__(self):
        return f"Bed {self.bed_number} ({self.ward.name})"

    def save(self, *args, **kwargs):
        if not self.bed_number and self.ward_id:
            self.bed_number = self._generate_next_bed_number()
        self.sync_occupancy_fields()
        super().save(*args, **kwargs)

    @property
    def active_assignment(self):
        return getattr(self, "_prefetched_active_assignment", None) or self.assignments.filter(
            status__in=["reserved", "active"],
            archived_at__isnull=True,
        ).order_by("-start_time").first()

    def derive_status(self) -> str:
        if self.blocked_reason:
            return "blocked"
        if self.cleaning_status in {"needs_cleaning", "cleaning_in_progress"}:
            return "cleaning"
        active_assignment = self.active_assignment
        if active_assignment and active_assignment.status == "active":
            return "occupied"
        if active_assignment and active_assignment.status == "reserved":
            return "reserved"
        if self.status == "maintenance":
            return "maintenance"
        return "available"

    def sync_occupancy_fields(self):
        active_assignment = self.active_assignment
        self.status = self.derive_status()
        if active_assignment and active_assignment.status == "active":
            self.patient_id = str(active_assignment.patient_id)
            self.occupied_since = active_assignment.start_time
        else:
            self.patient_id = None
            self.occupied_since = None

    def _generate_next_bed_number(self) -> str:
        existing_numbers = (
            Bed.objects
            .filter(ward_id=self.ward_id)
            .exclude(pk=self.pk)
            .values_list("bed_number", flat=True)
        )
        last_number = 0
        for value in existing_numbers:
            if not value:
                continue
            match = re.search(r"(\d+)$", str(value))
            if match:
                last_number = max(last_number, int(match.group(1)))
        return f"{last_number + 1:03d}"


class BedAssignment(models.Model):
    STATUS_CHOICES = [
        ("reserved", "Reserved"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="bed_assignments",
    )
    encounter = models.ForeignKey(
        "patients.Encounter",
        on_delete=models.PROTECT,
        related_name="bed_assignments",
    )
    bed = models.ForeignKey(
        Bed,
        on_delete=models.PROTECT,
        related_name="assignments",
    )
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    assigned_by = models.CharField(max_length=255, blank=True, default="")
    notes = models.TextField(blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bed_assignments"
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["bed", "status"]),
            models.Index(fields=["patient", "status"]),
            models.Index(fields=["encounter", "status"]),
        ]

    def __str__(self):
        return f"{self.patient_id} -> {self.bed_id} ({self.status})"
