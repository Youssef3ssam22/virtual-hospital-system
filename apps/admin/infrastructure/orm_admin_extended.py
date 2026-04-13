"""Admin Permissions and Audit models."""
import uuid
import json
from decimal import Decimal
from django.db import models


class Permission(models.Model):
    """Custom permission model."""

    ACTION_CHOICES = [
        ("view", "View"),
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("approve", "Approve"),
        ("assign", "Assign"),
        ("configure", "Configure"),
        ("export", "Export"),
        ("manage", "Manage"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    module = models.CharField(max_length=50)  # admin, patients, lab, pharmacy, billing
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default="view")
    scope = models.CharField(max_length=50, default="global")
    is_sensitive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'permissions'
        ordering = ['module', 'name']

    def __str__(self):
        return f"{self.name} ({self.module})"


class Role(models.Model):
    """Role model."""

    ROLE_CATEGORY_CHOICES = [
        ("system", "System"),
        ("administration", "Administration"),
        ("clinical", "Clinical"),
        ("operations", "Operations"),
        ("revenue_cycle", "Revenue Cycle"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=30, choices=ROLE_CATEGORY_CHOICES, default="administration")
    permissions = models.ManyToManyField(Permission, related_name='roles')
    is_system_role = models.BooleanField(default=False)  # Can't be deleted
    is_assignable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'
        ordering = ['name']

    def __str__(self):
        return self.name


class AuditLog(models.Model):
    """Audit log model for tracking user actions."""

    OUTCOME_CHOICES = [
        ("success", "Success"),
        ("failure", "Failure"),
        ("warning", "Warning"),
        ("info", "Info"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    actor_id = models.CharField(max_length=255)  # User ID
    actor_role = models.CharField(max_length=100)  # User's role
    action = models.CharField(max_length=100, db_index=True)
    source_module = models.CharField(max_length=100, blank=True, default="")
    entity_type = models.CharField(max_length=100)  # Department, Ward, Patient, etc.
    entity_id = models.CharField(max_length=500, blank=True)
    detail = models.JSONField(null=True, blank=True)
    reason = models.TextField(blank=True, default="")
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, blank=True, default="info")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['actor_id', '-occurred_at']),
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['action', '-occurred_at']),
        ]

    def __str__(self):
        return f"{self.action} on {self.entity_type} by {self.actor_id}"


class SystemSettings(models.Model):
    """System-wide settings."""

    CATEGORY_CHOICES = [
        ("hospital_profile", "Hospital Profile"),
        ("bed_management", "Bed Management"),
        ("billing", "Billing"),
        ("security", "Security"),
        ("notifications", "Notifications"),
        ("integrations", "Integrations"),
        ("operations", "Operations"),
    ]

    DATA_TYPE_CHOICES = [
        ("string", "String"),
        ("integer", "Integer"),
        ("decimal", "Decimal"),
        ("boolean", "Boolean"),
        ("json", "JSON"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="operations")
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES, default="string")
    is_public = models.BooleanField(default=False)
    is_sensitive = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'system_settings'
        verbose_name_plural = "System Settings"

    def __str__(self):
        return self.key

    @classmethod
    def get_setting(cls, key: str, default=None):
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default

    @classmethod
    def get_typed_value(cls, key: str, default=None):
        try:
            setting = cls.objects.get(key=key)
        except cls.DoesNotExist:
            return default

        raw_value = setting.value
        if raw_value in (None, ""):
            return default

        try:
            if setting.data_type == "boolean":
                return str(raw_value).strip().lower() in {"1", "true", "yes", "on"}
            if setting.data_type == "integer":
                return int(raw_value)
            if setting.data_type == "decimal":
                return Decimal(str(raw_value))
            if setting.data_type == "json":
                return json.loads(raw_value)
            return raw_value
        except (TypeError, ValueError, json.JSONDecodeError, ArithmeticError):
            return default


class UserRole(models.Model):
    """User-Role mapping model."""

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("expired", "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.CharField(max_length=255)  # References User
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    scope_department = models.ForeignKey(
        "hospital_administration.Department",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="user_roles",
    )
    scope_ward = models.ForeignKey(
        "hospital_administration.Ward",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="user_roles",
    )
    is_primary = models.BooleanField(default=False)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.CharField(max_length=255)  # Admin who assigned

    class Meta:
        db_table = 'user_roles'
        unique_together = ('user_id', 'role')

    def __str__(self):
        return f"{self.user_id} - {self.role.name}"
