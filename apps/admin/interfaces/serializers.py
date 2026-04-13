"""Admin serializers for Department, Ward, and Bed."""
from rest_framework import serializers
from apps.admin.infrastructure.orm_admin_models import Department, Ward, Bed, BedAssignment
from apps.admin.infrastructure.orm_models import AdminUser


class DepartmentSerializer(serializers.ModelSerializer):
    """Department serializer."""
    
    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'code',
            'department_type',
            'description',
            'head_id',
            'manager_name',
            'location',
            'floor',
            'extension_phone',
            'operating_hours',
            'is_clinical',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_code(self, value):
        """Validate code is unique (case-insensitive)."""
        queryset = Department.objects.filter(code__iexact=value)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Department code must be unique.")
        return value.upper()
    
    def validate_name(self, value):
        """Validate name is not empty."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Department name cannot be empty.")
        return value.strip()


class WardSerializer(serializers.ModelSerializer):
    """Ward serializer."""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Ward
        fields = [
            'id',
            'name',
            'code',
            'department',
            'department_name',
            'type',
            'gender_restriction',
            'age_group',
            'specialty',
            'nurse_station',
            'supports_isolation',
            'total_beds',
            'available_beds',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_code(self, value):
        """Validate code is unique."""
        queryset = Ward.objects.filter(code__iexact=value)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Ward code must be unique.")
        return value.upper()
    
    def validate(self, data):
        """Validate total_beds >= available_beds."""
        total_beds = data.get('total_beds', getattr(self.instance, 'total_beds', 0))
        available_beds = data.get('available_beds', getattr(self.instance, 'available_beds', 0))
        if available_beds > total_beds:
            raise serializers.ValidationError(
                "Available beds cannot exceed total beds."
            )
        return data


class BedSerializer(serializers.ModelSerializer):
    """Bed serializer."""
    
    ward_name = serializers.CharField(source='ward.name', read_only=True)
    bed_number = serializers.CharField(required=False, allow_blank=True)
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Bed
        fields = [
            'id',
            'room_number',
            'bed_number',
            'ward',
            'ward_name',
            'type',
            'bed_class',
            'features',
            'status',
            'cleaning_status',
            'blocked_reason',
            'patient_id',
            'occupied_since',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'occupied_since', 'status', 'patient_id']
    
    def validate_features(self, value):
        """Validate features is a list."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Features must be a list.")
        valid_features = {'oxygen', 'monitor', 'ventilator', 'suction', 'iv_stand'}
        invalid = set(value) - valid_features
        if invalid:
            raise serializers.ValidationError(
                f"Invalid features: {invalid}. "
                f"Valid features are: {valid_features}"
            )
        return value

    def get_status(self, obj):
        return obj.derive_status()

    def validate(self, data):
        status_value = getattr(self.instance, "status", "available")
        blocked_reason = data.get("blocked_reason", getattr(self.instance, "blocked_reason", ""))
        if status_value == "blocked" and not blocked_reason:
            raise serializers.ValidationError("Blocked beds must include a blocked_reason.")
        return data


class BedAssignmentSerializer(serializers.ModelSerializer):
    bed_number = serializers.CharField(source="bed.bed_number", read_only=True)
    ward_name = serializers.CharField(source="bed.ward.name", read_only=True)

    class Meta:
        model = BedAssignment
        fields = [
            "id",
            "patient",
            "encounter",
            "bed",
            "bed_number",
            "ward_name",
            "start_time",
            "end_time",
            "status",
            "assigned_by",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        start_time = data.get("start_time", getattr(self.instance, "start_time", None))
        end_time = data.get("end_time", getattr(self.instance, "end_time", None))
        bed = data.get("bed", getattr(self.instance, "bed", None))
        encounter = data.get("encounter", getattr(self.instance, "encounter", None))
        status_value = data.get("status", getattr(self.instance, "status", "active"))

        if end_time and start_time and end_time < start_time:
            raise serializers.ValidationError("end_time must be on or after start_time.")
        if bed and encounter and encounter.status != "active":
            raise serializers.ValidationError("Encounter must be active before assigning a bed.")
        if bed and bed.assignments.exclude(pk=getattr(self.instance, "pk", None)).filter(
            status__in=["reserved", "active"],
            archived_at__isnull=True,
        ).exists():
            raise serializers.ValidationError("This bed already has an active or reserved assignment.")
        if status_value == "completed" and not end_time:
            raise serializers.ValidationError("Completed bed assignments require end_time.")
        return data


class AdminUserSerializer(serializers.ModelSerializer):
    """Admin user serializer."""

    status = serializers.SerializerMethodField()
    status_update = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = AdminUser
        fields = [
            'id',
            'employee_number',
            'email',
            'full_name',
            'phone',
            'role',
            'department_id',
            'status',
            'status_update',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']

    def get_status(self, obj):
        return 'active' if obj.is_active else 'inactive'

    def validate_status_update(self, value):
        allowed = {'active', 'inactive', 'suspended'}
        if value not in allowed:
            raise serializers.ValidationError(f"status must be one of {allowed}")
        return value

    def update(self, instance, validated_data):
        status_update = validated_data.pop('status_update', None)
        if status_update:
            instance.is_active = status_update == 'active'
        return super().update(instance, validated_data)
