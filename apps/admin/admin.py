"""Django admin configuration for Admin module."""
from django.contrib import admin

from apps.admin.infrastructure.orm_admin_models import Department, Ward, Bed, BedAssignment
from apps.admin.infrastructure.orm_admin_extended import (
    Permission, Role, AuditLog, SystemSettings, UserRole,
)
from apps.admin.infrastructure.orm_catalog_models import (
    LabCatalogItem, RadiologyCatalogItem, ServiceCatalogItem,
)
from apps.admin.infrastructure.orm_models import AdminUser, SystemConfig


@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ("employee_number", "full_name", "email", "role", "is_active", "created_at")
    list_filter = ("role", "is_active", "created_at")
    search_fields = ("employee_number", "full_name", "email")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ("key", "updated_at", "updated_by")
    search_fields = ("key", "description")
    ordering = ("key",)
    readonly_fields = ("updated_at",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "department_type",
        "manager_name",
        "location",
        "is_clinical",
        "status",
    )
    list_filter = ("department_type", "is_clinical", "status")
    search_fields = ("name", "code", "description", "manager_name", "location")
    ordering = ("name",)
    readonly_fields = ("id", "created_at", "updated_at")
    list_per_page = 20
    fieldsets = (
        ("Department Identity", {"fields": ("code", "name", "department_type", "description", "status")}),
        ("Operations", {"fields": ("manager_name", "head_id", "is_clinical", "operating_hours")}),
        ("Location", {"fields": ("location", "floor", "extension_phone")}),
        ("System", {"fields": ("id", "created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "department",
        "type",
        "gender_restriction",
        "age_group",
        "total_beds",
        "available_beds",
        "status",
    )
    list_filter = ("department", "type", "gender_restriction", "age_group", "supports_isolation", "status")
    search_fields = ("name", "code", "specialty", "nurse_station")
    ordering = ("department__name", "name")
    readonly_fields = ("id", "created_at", "updated_at")
    list_per_page = 20
    list_select_related = ("department",)
    fieldsets = (
        ("Ward Identity", {"fields": ("department", "code", "name", "type", "status")}),
        ("Clinical Profile", {"fields": ("specialty", "gender_restriction", "age_group", "supports_isolation")}),
        ("Capacity", {"fields": ("total_beds", "available_beds", "nurse_station")}),
        ("System", {"fields": ("id", "created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = (
        "room_number",
        "bed_number",
        "ward",
        "type",
        "bed_class",
        "status",
        "cleaning_status",
        "patient_id",
    )
    list_filter = ("ward", "type", "bed_class", "status", "cleaning_status")
    search_fields = ("room_number", "bed_number", "patient_id")
    ordering = ("ward__name", "room_number", "bed_number")
    readonly_fields = ("id", "occupied_since", "created_at", "updated_at")
    list_per_page = 25
    list_select_related = ("ward",)
    fieldsets = (
        ("Bed Identity", {"fields": ("ward", "room_number", "bed_number", "type", "bed_class")}),
        ("Operational Status", {"fields": ("status", "cleaning_status", "blocked_reason", "patient_id", "occupied_since")}),
        ("Capabilities", {"fields": ("features",)}),
        ("System", {"fields": ("id", "created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(BedAssignment)
class BedAssignmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "encounter", "bed", "status", "start_time", "end_time")
    list_filter = ("status", "bed__ward")
    search_fields = ("patient__full_name", "patient__mrn", "bed__bed_number")
    ordering = ("-start_time",)
    readonly_fields = ("id", "created_at", "updated_at")
    list_select_related = ("patient", "encounter", "bed", "bed__ward")


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "module", "action", "scope", "is_sensitive")
    list_filter = ("module", "action", "scope", "is_sensitive")
    search_fields = ("name", "code", "description")
    ordering = ("module", "action", "name")
    readonly_fields = ("id", "created_at")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "category", "is_system_role", "is_assignable", "created_at")
    list_filter = ("category", "is_system_role", "is_assignable")
    search_fields = ("name", "code", "description")
    ordering = ("name",)
    readonly_fields = ("id", "created_at", "updated_at")
    filter_horizontal = ("permissions",)
    list_per_page = 20

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_system_role:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("occurred_at", "actor_id", "actor_role", "action", "source_module", "entity_type", "outcome")
    list_filter = ("action", "actor_role", "source_module", "entity_type", "outcome")
    search_fields = ("actor_id", "entity_id", "entity_type", "reason")
    ordering = ("-occurred_at",)
    readonly_fields = (
        "id",
        "actor_id",
        "actor_role",
        "action",
        "source_module",
        "entity_type",
        "entity_id",
        "detail",
        "reason",
        "outcome",
        "ip_address",
        "occurred_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ("key", "category", "data_type", "is_sensitive", "is_public", "updated_at")
    list_filter = ("category", "data_type", "is_sensitive", "is_public")
    search_fields = ("key", "description", "value")
    ordering = ("category", "key")
    readonly_fields = ("id", "updated_at")
    list_per_page = 25
    fieldsets = (
        ("Setting", {"fields": ("category", "key", "description")}),
        ("Value", {"fields": ("data_type", "value", "is_public", "is_sensitive")}),
        ("System", {"fields": ("id", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = (
        "user_id",
        "role",
        "status",
        "is_primary",
        "scope_department",
        "scope_ward",
        "effective_from",
        "effective_to",
        "assigned_at",
    )
    list_filter = ("role", "status", "is_primary", "scope_department")
    search_fields = ("user_id", "assigned_by")
    ordering = ("-assigned_at",)
    readonly_fields = ("id", "assigned_at")


@admin.register(LabCatalogItem)
class LabCatalogItemAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "department",
        "specimen_type",
        "turnaround_time_minutes",
        "stat_available",
        "price",
        "is_active",
    )
    list_filter = ("department", "specimen_type", "processing_site", "stat_available", "is_active")
    search_fields = ("code", "name", "description", "sample_container")
    ordering = ("code",)
    readonly_fields = ("id", "created_at", "updated_at")
    list_per_page = 25
    list_select_related = ("department",)


@admin.register(RadiologyCatalogItem)
class RadiologyCatalogItemAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "department",
        "modality",
        "body_part",
        "contrast_required",
        "price",
        "is_active",
    )
    list_filter = ("department", "modality", "contrast_required", "sedation_required", "is_active")
    search_fields = ("code", "name", "description", "body_part")
    ordering = ("code",)
    readonly_fields = ("id", "created_at", "updated_at")
    list_per_page = 25
    list_select_related = ("department",)


@admin.register(ServiceCatalogItem)
class ServiceCatalogItemAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "department",
        "category",
        "service_class",
        "revenue_code",
        "billing_type",
        "requires_physician_order",
        "requires_bed_assignment",
        "package_eligible",
        "price",
        "is_active",
    )
    list_filter = ("department", "category", "service_class", "billing_type", "requires_physician_order", "package_eligible", "is_active")
    search_fields = ("code", "name", "description", "insurance_category", "revenue_code")
    ordering = ("code",)
    readonly_fields = ("id", "created_at", "updated_at")
    list_per_page = 25
    list_select_related = ("department",)
    fieldsets = (
        ("Service Identity", {"fields": ("department", "code", "name", "description", "category", "service_class")}),
        ("Billing Rules", {"fields": ("billing_type", "revenue_code", "insurance_category", "package_eligible", "price")}),
        ("Operational Rules", {"fields": ("requires_physician_order", "requires_result_entry", "requires_bed_assignment", "service_duration_minutes")}),
        ("System", {"fields": ("is_active", "id", "created_at", "updated_at"), "classes": ("collapse",)}),
    )
