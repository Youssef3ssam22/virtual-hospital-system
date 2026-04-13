"""Admin API routes."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AdminActivationView,
    AdminDetailView,
    AdminListCreateView,
)
from .views_extended import DepartmentViewSet, WardViewSet, BedViewSet, BedAssignmentViewSet
from .views_advanced import (
    PermissionViewSet, RoleViewSet, AuditLogViewSet,
    SystemSettingsViewSet, UserRoleViewSet,
    AdminUserViewSet, LabCatalogItemViewSet, RadiologyCatalogItemViewSet,
    ServiceCatalogItemViewSet, AdminStatsView
)

# Create router for auto-generated endpoints
router = DefaultRouter(trailing_slash=False)
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'wards', WardViewSet, basename='ward')
router.register(r'beds', BedViewSet, basename='bed')
router.register(r'bed-assignments', BedAssignmentViewSet, basename='bed-assignment')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'settings', SystemSettingsViewSet, basename='setting')
router.register(r'user-roles', UserRoleViewSet, basename='user-role')
router.register(r'users', AdminUserViewSet, basename='admin-user')
router.register(r'catalogs/lab', LabCatalogItemViewSet, basename='lab-catalog')
router.register(r'catalogs/radiology', RadiologyCatalogItemViewSet, basename='radiology-catalog')
router.register(r'catalogs/services', ServiceCatalogItemViewSet, basename='service-catalog')

urlpatterns = [
    path("admins/", AdminListCreateView.as_view(), name="admin-list-create"),
    path("admins/<uuid:admin_id>/", AdminDetailView.as_view(), name="admin-detail"),
    path("admins/<uuid:admin_id>/<str:action>/", AdminActivationView.as_view(), name="admin-activation"),
    path("stats/", AdminStatsView.as_view(), name="admin-stats"),
    path("", include(router.urls)),
]
