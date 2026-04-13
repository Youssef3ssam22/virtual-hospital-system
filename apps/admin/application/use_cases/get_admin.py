"""Read use cases for admin data retrieval."""

from shared.domain.exceptions import EntityNotFound

from apps.admin.domain.repositories import AdminRepository


class GetAdminUseCase:
    """Get admin users and system configuration."""

    def __init__(self, repository: AdminRepository):
        self.repository = repository

    def by_id(self, admin_id: str):
        """Get admin user by ID."""
        admin = self.repository.get_by_id(admin_id)
        if not admin:
            raise EntityNotFound("Admin", admin_id)
        return admin

    def list_all(self, *, active_only: bool = False):
        """List all admin users."""
        return self.repository.list(active_only=active_only)

    def get_system_config(self):
        """Get system-wide configuration."""
        return self.repository.get_config()

    def get_audit_logs(self, *, limit: int = 100):
        """Get recent audit logs."""
        return self.repository.get_audit_logs(limit=limit)
