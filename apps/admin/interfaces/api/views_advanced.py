"""Admin API views for Roles, Audit Logs, and Settings."""
from datetime import date, timedelta

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models
from django.utils import timezone
from shared.permissions import (
    CanAssignUserRoles,
    CanManageAdminUsers,
    CanManageLabCatalog,
    CanManageRadiologyCatalog,
    CanManageRoles,
    CanManageServiceCatalog,
    CanManageSystemSettings,
    CanReadAuditLogs,
)

from apps.admin.infrastructure.orm_admin_extended import (
    Permission, Role, AuditLog, SystemSettings, UserRole
)
from apps.admin.infrastructure.orm_admin_models import Department, Ward, Bed, BedAssignment
from apps.admin.infrastructure.orm_models import AdminUser
from apps.admin.infrastructure.orm_catalog_models import (
    LabCatalogItem, RadiologyCatalogItem, ServiceCatalogItem
)
from apps.admin.interfaces.serializers import AdminUserSerializer
from apps.admin.interfaces.serializers_extended import (
    PermissionSerializer, RoleSerializer, AuditLogSerializer,
    SystemSettingsSerializer, UserRoleSerializer,
    LabCatalogItemSerializer, RadiologyCatalogItemSerializer, ServiceCatalogItemSerializer
)
from apps.auth.infrastructure.orm_models import User
from infrastructure.audit.audit_logger import AuditLogger, AuditAction


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """Permission management (read-only)."""
    
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [CanManageRoles]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['module', 'action', 'scope', 'is_sensitive']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['module', 'action', 'name']
    ordering = ['module', 'name']

    @action(detail=False, methods=['put'])
    def bulk_update(self, request):
        """Bulk update permissions."""
        if not isinstance(request.data, list):
            return Response({'detail': 'Expected a list of permissions.'}, status=status.HTTP_400_BAD_REQUEST)

        updated = []
        for item in request.data:
            perm_id = item.get('id')
            if not perm_id:
                continue
            try:
                perm = Permission.objects.get(id=perm_id)
            except Permission.DoesNotExist:
                continue
            serializer = PermissionSerializer(perm, data=item, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            updated.append(serializer.data)

        return Response(updated, status=status.HTTP_200_OK)


class RoleViewSet(viewsets.ModelViewSet):
    """Role management viewset."""
    
    queryset = Role.objects.prefetch_related('permissions')
    serializer_class = RoleSerializer
    permission_classes = [CanManageRoles]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_system_role', 'is_assignable']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at', 'category']
    ordering = ['name']
    
    def perform_destroy(self, instance):
        """Prevent deletion of system roles."""
        if instance.is_system_role:
            raise PermissionDenied("Cannot delete system roles.")
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def list_system_roles(self, request):
        """List all system roles."""
        roles = Role.objects.filter(is_system_role=True)
        serializer = self.get_serializer(roles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_permission(self, request, pk=None):
        """Add permission to role."""
        role = self.get_object()
        permission_id = request.data.get('permission_id')
        
        try:
            permission = Permission.objects.get(id=permission_id)
            role.permissions.add(permission)
            return Response(
                RoleSerializer(role).data,
                status=status.HTTP_200_OK
            )
        except Permission.DoesNotExist:
            return Response(
                {'detail': 'Permission not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_permission(self, request, pk=None):
        """Remove permission from role."""
        role = self.get_object()
        permission_id = request.data.get('permission_id')
        
        try:
            permission = Permission.objects.get(id=permission_id)
            role.permissions.remove(permission)
            return Response(
                RoleSerializer(role).data,
                status=status.HTTP_200_OK
            )
        except Permission.DoesNotExist:
            return Response(
                {'detail': 'Permission not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Audit log viewing (read-only)."""
    
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [CanReadAuditLogs]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['actor_id', 'action', 'entity_type', 'source_module', 'outcome']
    ordering_fields = ['occurred_at']
    ordering = ['-occurred_at']
    
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Get audit logs by specific user."""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'detail': 'user_id parameter required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logs = AuditLog.objects.filter(actor_id=user_id).order_by('-occurred_at')
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_entity(self, request):
        """Get audit logs for specific entity."""
        entity_type = request.query_params.get('entity_type')
        entity_id = request.query_params.get('entity_id')
        
        if not entity_type or not entity_id:
            return Response(
                {'detail': 'entity_type and entity_id parameters required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logs = AuditLog.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id
        ).order_by('-occurred_at')
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent audit logs (last 24 hours)."""
        since = timezone.now() - timedelta(hours=24)
        logs = AuditLog.objects.filter(occurred_at__gte=since).order_by('-occurred_at')
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get audit log summary."""
        return Response({
            'total_logs': AuditLog.objects.count(),
            'actions_breakdown': dict(
                AuditLog.objects.values('action')
                .annotate(count=models.Count('id'))
                .values_list('action', 'count')
            ),
            'logs_per_day': dict(
                AuditLog.objects.extra(
                    select={'date': 'DATE(occurred_at)'}
                )
                .values('date')
                .annotate(count=models.Count('id'))
                .values_list('date', 'count')
            )
        })


class SystemSettingsViewSet(viewsets.ModelViewSet):
    """System settings management."""
    
    queryset = SystemSettings.objects.all()
    serializer_class = SystemSettingsSerializer
    permission_classes = [CanManageSystemSettings]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['key', 'description', 'category']
    ordering_fields = ['key', 'updated_at', 'category']
    ordering = ['key']
    
    def get_queryset(self):
        """All settings are available because this viewset is admin-only."""
        return SystemSettings.objects.all()
    
    @action(detail=False, methods=['get'])
    def by_key(self, request):
        """Get specific setting by key."""
        key = request.query_params.get('key')
        if not key:
            return Response(
                {'detail': 'key parameter required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            setting = SystemSettings.objects.get(key__iexact=key)
            return Response(
                SystemSettingsSerializer(setting).data,
                status=status.HTTP_200_OK
            )
        except SystemSettings.DoesNotExist:
            return Response(
                {'detail': 'Setting not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserRoleViewSet(viewsets.ModelViewSet):
    """User-Role assignment management."""
    
    queryset = UserRole.objects.select_related('role', 'scope_department', 'scope_ward')
    serializer_class = UserRoleSerializer
    permission_classes = [CanAssignUserRoles]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['user_id', 'role', 'status', 'is_primary', 'scope_department', 'scope_ward']
    ordering_fields = ['assigned_at']
    ordering = ['-assigned_at']
    
    @action(detail=False, methods=['post'])
    def assign_role_to_user(self, request):
        """Assign role to user."""
        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')
        scope_department_id = request.data.get('scope_department_id')
        scope_ward_id = request.data.get('scope_ward_id')
        is_primary = bool(request.data.get('is_primary', False))
        effective_from = request.data.get('effective_from')
        effective_to = request.data.get('effective_to')

        if not user_id or not role_id:
            return Response(
                {'detail': 'user_id and role_id required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already assigned
        if UserRole.objects.filter(user_id=user_id, role_id=role_id).exists():
            return Response(
                {'detail': 'User already has this role.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            role = Role.objects.get(id=role_id)
            scope_department = Department.objects.filter(id=scope_department_id).first() if scope_department_id else None
            scope_ward = Ward.objects.filter(id=scope_ward_id).first() if scope_ward_id else None
            effective_from_value = date.fromisoformat(effective_from) if effective_from else None
            effective_to_value = date.fromisoformat(effective_to) if effective_to else None

            if scope_department_id and scope_department is None:
                return Response(
                    {'detail': 'scope_department_id was not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            if scope_ward_id and scope_ward is None:
                return Response(
                    {'detail': 'scope_ward_id was not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            if effective_from_value and effective_to_value and effective_to_value < effective_from_value:
                return Response(
                    {'detail': 'effective_to must be on or after effective_from.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if is_primary:
                UserRole.objects.filter(user_id=user_id, is_primary=True).update(is_primary=False)

            user_role = UserRole.objects.create(
                user_id=user_id,
                role=role,
                scope_department=scope_department,
                scope_ward=scope_ward,
                is_primary=is_primary,
                effective_from=effective_from_value,
                effective_to=effective_to_value,
                status='active',
                assigned_by=str(request.user.id) if hasattr(request.user, 'id') else 'system'
            )
            return Response(
                UserRoleSerializer(user_role).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError:
            return Response(
                {'detail': 'effective_from and effective_to must be valid ISO dates.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Role.DoesNotExist:
            return Response(
                {'detail': 'Role not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['delete'])
    def remove_user_role(self, request, pk=None):
        """Remove role from user."""
        user_role = self.get_object()
        user_role.delete()
        return Response(
            {'detail': 'Role removed from user.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def user_roles(self, request):
        """Get all roles for a user."""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'detail': 'user_id parameter required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_roles = UserRole.objects.filter(user_id=user_id).select_related('role', 'scope_department', 'scope_ward')
        serializer = self.get_serializer(user_roles, many=True)
        return Response(serializer.data)


class AdminUserViewSet(viewsets.ModelViewSet):
    """Admin user management (API-level)."""

    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [CanManageAdminUsers]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['full_name', 'email', 'employee_number']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post', 'put'])
    def status(self, request, pk=None):
        """Activate or deactivate admin user."""
        admin_user = self.get_object()
        status_value = request.data.get('status')
        if status_value not in ['active', 'inactive', 'suspended']:
            return Response({'detail': 'status must be active, inactive, or suspended.'}, status=400)
        admin_user.is_active = status_value == 'active'
        admin_user.save(update_fields=['is_active', 'updated_at'])
        return Response(AdminUserSerializer(admin_user).data)

    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        """Force reset password for the linked auth user by email."""
        admin_user = self.get_object()
        temp_password = _generate_temp_password()
        user, created = User.objects.get_or_create(
            email=admin_user.email,
            defaults={
                'full_name': admin_user.full_name,
                'is_active': True,
                'is_staff': True,
                'is_superuser': False,
            },
        )
        user.set_password(temp_password)
        user.save()

        AuditLogger().log(
            actor_id=str(request.user.id) if hasattr(request.user, 'id') else 'system',
            actor_role=getattr(request.user, 'role', 'UNKNOWN'),
            action=AuditAction.PASSWORD_RESET_COMPLETED,
            source_module='admin.user_management',
            entity_type='AdminUser',
            entity_id=str(admin_user.id),
            detail={'email': admin_user.email},
            reason='Administrative password reset from admin console.',
            outcome='success',
        )

        return Response({'detail': 'Password reset successful.', 'temp_password': temp_password})

    @action(detail=True, methods=['get'])
    def activity(self, request, pk=None):
        """Recent audit log entries for admin user."""
        admin_user = self.get_object()
        logs = AuditLog.objects.filter(actor_id=str(admin_user.id)).order_by('-occurred_at')[:50]
        return Response(AuditLogSerializer(logs, many=True).data)


class LabCatalogItemViewSet(viewsets.ModelViewSet):
    """Lab test catalog management."""

    queryset = LabCatalogItem.objects.all()
    serializer_class = LabCatalogItemSerializer
    permission_classes = [CanManageLabCatalog]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['department', 'specimen_type', 'processing_site', 'stat_available', 'is_active']
    search_fields = ['code', 'name', 'description', 'sample_container']
    ordering_fields = ['code', 'created_at']
    ordering = ['code']


class RadiologyCatalogItemViewSet(viewsets.ModelViewSet):
    """Radiology exam catalog management."""

    queryset = RadiologyCatalogItem.objects.all()
    serializer_class = RadiologyCatalogItemSerializer
    permission_classes = [CanManageRadiologyCatalog]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['department', 'modality', 'contrast_required', 'sedation_required', 'is_active']
    search_fields = ['code', 'name', 'body_part', 'description']
    ordering_fields = ['code', 'created_at']
    ordering = ['code']


class ServiceCatalogItemViewSet(viewsets.ModelViewSet):
    """General service catalog management."""

    queryset = ServiceCatalogItem.objects.all()
    serializer_class = ServiceCatalogItemSerializer
    permission_classes = [CanManageServiceCatalog]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['department', 'category', 'service_class', 'billing_type', 'package_eligible', 'requires_physician_order', 'is_active']
    search_fields = ['code', 'name', 'description', 'insurance_category', 'revenue_code']
    ordering_fields = ['code', 'created_at']
    ordering = ['code']


class AdminStatsView(APIView):
    """Admin stats dashboard."""

    permission_classes = [CanReadAuditLogs]

    def get(self, request):
        from apps.lab.infrastructure.orm_models import LabResult
        total_users = AdminUser.objects.count()
        active_users = AdminUser.objects.filter(is_active=True).count()
        total_departments = Department.objects.count()
        total_wards = Ward.objects.count()
        total_beds = Bed.objects.count()
        occupied_beds = BedAssignment.objects.filter(status='active', archived_at__isnull=True).count()
        blocked_beds = Bed.objects.filter(blocked_reason__gt='').count()
        cleaning_beds = Bed.objects.filter(cleaning_status__in=['needs_cleaning', 'cleaning_in_progress']).count()
        total_lab_tests = LabResult.objects.count()
        audit_logs_today = AuditLog.objects.filter(
            occurred_at__date=timezone.now().date()
        ).count()

        return Response({
            'totalUsers': total_users,
            'activeUsers': active_users,
            'totalDepartments': total_departments,
            'totalWards': total_wards,
            'totalBeds': total_beds,
            'occupiedBeds': occupied_beds,
            'blockedBeds': blocked_beds,
            'cleaningBeds': cleaning_beds,
            'totalLabTests': total_lab_tests,
            'auditLogsToday': audit_logs_today,
            'systemUptime': None,
        })


def _generate_temp_password() -> str:
    import secrets
    return f"Temp@{secrets.token_hex(4)}"
