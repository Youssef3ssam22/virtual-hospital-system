"""Admin extended serializers for Roles, Audit Logs, and Settings."""
import json
from decimal import Decimal, InvalidOperation

from rest_framework import serializers
from apps.admin.infrastructure.orm_admin_extended import (
    Permission, Role, AuditLog, SystemSettings, UserRole
)
from apps.admin.infrastructure.orm_catalog_models import (
    LabCatalogItem, RadiologyCatalogItem, ServiceCatalogItem
)


class PermissionSerializer(serializers.ModelSerializer):
    """Permission serializer."""

    class Meta:
        model = Permission
        fields = ['id', 'name', 'code', 'description', 'module', 'action', 'scope', 'is_sensitive', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_code(self, value):
        return value.upper()


class RoleSerializer(serializers.ModelSerializer):
    """Role serializer."""
    
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        write_only=True,
        many=True,
        source='permissions'
    )
    
    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'code',
            'description',
            'category',
            'permissions',
            'permission_ids',
            'is_system_role',
            'is_assignable',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'is_system_role', 'created_at', 'updated_at']
    
    def validate_code(self, value):
        """Validate code is unique."""
        queryset = Role.objects.filter(code__iexact=value)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Role code must be unique.")
        return value.upper()


class AuditLogSerializer(serializers.ModelSerializer):
    """Audit log serializer."""
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'actor_id',
            'actor_role',
            'action',
            'source_module',
            'entity_type',
            'entity_id',
            'detail',
            'reason',
            'outcome',
            'ip_address',
            'occurred_at',
        ]
        read_only_fields = fields


class SystemSettingsSerializer(serializers.ModelSerializer):
    """System settings serializer."""
    
    class Meta:
        model = SystemSettings
        fields = ['id', 'key', 'value', 'description', 'category', 'data_type', 'is_public', 'is_sensitive', 'updated_at']
        read_only_fields = ['id', 'updated_at']
    
    def validate_key(self, value):
        """Validate key format."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Setting key cannot be empty.")
        return value.upper()

    def validate(self, data):
        data_type = data.get('data_type', getattr(self.instance, 'data_type', 'string'))
        value = data.get('value', getattr(self.instance, 'value', ''))
        if data_type == 'integer':
            try:
                int(value)
            except (TypeError, ValueError):
                raise serializers.ValidationError("value must be an integer for integer settings.")
        elif data_type == 'decimal':
            try:
                Decimal(str(value))
            except (InvalidOperation, ValueError):
                raise serializers.ValidationError("value must be a decimal for decimal settings.")
        elif data_type == 'boolean':
            if str(value).strip().lower() not in {'true', 'false', '1', '0', 'yes', 'no', 'on', 'off'}:
                raise serializers.ValidationError("value must be boolean-like for boolean settings.")
        elif data_type == 'json':
            try:
                json.loads(value)
            except (TypeError, json.JSONDecodeError):
                raise serializers.ValidationError("value must be valid JSON for json settings.")
        return data


class UserRoleSerializer(serializers.ModelSerializer):
    """User-Role mapping serializer."""

    role_name = serializers.CharField(source='role.name', read_only=True)
    role_code = serializers.CharField(source='role.code', read_only=True)
    scope_department_name = serializers.CharField(source='scope_department.name', read_only=True)
    scope_ward_name = serializers.CharField(source='scope_ward.name', read_only=True)

    class Meta:
        model = UserRole
        fields = [
            'id',
            'user_id',
            'role',
            'role_name',
            'role_code',
            'scope_department',
            'scope_department_name',
            'scope_ward',
            'scope_ward_name',
            'is_primary',
            'effective_from',
            'effective_to',
            'status',
            'assigned_at',
            'assigned_by',
        ]
        read_only_fields = ['id', 'assigned_at']

    def validate(self, data):
        effective_from = data.get("effective_from", getattr(self.instance, "effective_from", None))
        effective_to = data.get("effective_to", getattr(self.instance, "effective_to", None))
        if effective_from and effective_to and effective_to < effective_from:
            raise serializers.ValidationError("effective_to must be on or after effective_from.")
        return data


class LabCatalogItemSerializer(serializers.ModelSerializer):
    """Lab test catalog serializer."""

    class Meta:
        model = LabCatalogItem
        fields = [
            'id',
            'code',
            'name',
            'description',
            'department',
            'specimen_type',
            'sample_container',
            'minimum_volume_ml',
            'default_unit',
            'fasting_required',
            'turnaround_time_minutes',
            'stat_available',
            'processing_site',
            'price',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RadiologyCatalogItemSerializer(serializers.ModelSerializer):
    """Radiology exam catalog serializer."""

    class Meta:
        model = RadiologyCatalogItem
        fields = [
            'id',
            'code',
            'name',
            'description',
            'department',
            'modality',
            'body_part',
            'contrast_required',
            'preparation_instructions',
            'duration_minutes',
            'sedation_required',
            'uses_radiation',
            'report_turnaround_minutes',
            'price',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceCatalogItemSerializer(serializers.ModelSerializer):
    """General service catalog serializer."""

    class Meta:
        model = ServiceCatalogItem
        fields = [
            'id',
            'code',
            'name',
            'description',
            'department',
            'category',
            'service_class',
            'revenue_code',
            'billing_type',
            'insurance_category',
            'package_eligible',
            'requires_physician_order',
            'requires_result_entry',
            'requires_bed_assignment',
            'service_duration_minutes',
            'price',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        category = data.get('category', getattr(self.instance, 'category', 'consultation'))
        billing_type = data.get('billing_type', getattr(self.instance, 'billing_type', 'fixed'))
        requires_bed_assignment = data.get(
            'requires_bed_assignment',
            getattr(self.instance, 'requires_bed_assignment', False),
        )

        if category == 'room' and billing_type != 'per_day':
            raise serializers.ValidationError("Room and bed services must use billing_type='per_day'.")
        if category == 'room' and not requires_bed_assignment:
            raise serializers.ValidationError("Room services must require bed assignment.")
        return data
