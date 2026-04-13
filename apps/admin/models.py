"""Model registry for the admin app."""
from apps.admin.infrastructure.orm_admin_models import Department, Ward, Bed, BedAssignment
from apps.admin.infrastructure.orm_admin_extended import Permission, Role, AuditLog, SystemSettings, UserRole
from apps.admin.infrastructure.orm_models import AdminUser, SystemConfig
from apps.admin.infrastructure.orm_catalog_models import LabCatalogItem, RadiologyCatalogItem, ServiceCatalogItem

__all__ = [
    'Department', 'Ward', 'Bed', 'BedAssignment',
    'Permission', 'Role', 'AuditLog', 'SystemSettings', 'UserRole',
    'AdminUser', 'SystemConfig',
    'LabCatalogItem', 'RadiologyCatalogItem', 'ServiceCatalogItem',
]
