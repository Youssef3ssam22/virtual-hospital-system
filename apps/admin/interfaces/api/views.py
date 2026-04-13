"""HTTP handlers for admin APIs."""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.permissions import CanManageAdminUsers

from apps.admin.application.use_cases.get_admin import GetAdminUseCase
from apps.admin.application.use_cases.manage_admin import (
    ManageAdminUseCase,
    UpdateAdminCommand,
)
from apps.admin.application.use_cases.register_admin import (
    RegisterAdminCommand,
    RegisterAdminUseCase,
)
from apps.admin.infrastructure.repositories import DjangoAdminRepository


def _repo() -> DjangoAdminRepository:
    return DjangoAdminRepository()


def _serialize_admin(admin) -> dict:
    return {
        "id": admin.id,
        "employee_number": admin.employee_number,
        "email": admin.email,
        "full_name": admin.full_name,
        "role": str(admin.role),
        "department_id": admin.department_id,
        "phone": admin.phone,
        "is_active": admin.is_active,
    }


class AdminListCreateView(APIView):
    """GET list admins, POST register admin."""

    permission_classes = [CanManageAdminUsers]

    def get(self, request):
        use_case = GetAdminUseCase(_repo())
        active_only = str(request.query_params.get("active_only", "false")).lower() == "true"
        admins = use_case.list_all(active_only=active_only)
        payload = [_serialize_admin(item) for item in admins]
        return Response(payload)

    def post(self, request):
        command = RegisterAdminCommand(
            employee_number=request.data.get("employee_number"),
            email=request.data.get("email"),
            full_name=request.data.get("full_name"),
            role=request.data.get("role", "ADMIN"),
            department_id=request.data.get("department_id"),
            phone=request.data.get("phone"),
            actor_id=str(request.user.id),
            actor_role=getattr(request.user, "role", "UNKNOWN"),
        )
        created = RegisterAdminUseCase(_repo()).execute(command)
        return Response(_serialize_admin(created), status=status.HTTP_201_CREATED)


class AdminDetailView(APIView):
    """GET and PATCH a single admin."""

    permission_classes = [CanManageAdminUsers]

    def get(self, request, admin_id: str):
        admin = GetAdminUseCase(_repo()).by_id(admin_id)
        return Response(_serialize_admin(admin))

    def patch(self, request, admin_id: str):
        command = UpdateAdminCommand(
            admin_id=admin_id,
            full_name=request.data.get("full_name"),
            email=request.data.get("email"),
            phone=request.data.get("phone"),
            role=request.data.get("role"),
            actor_id=str(request.user.id),
            actor_role=getattr(request.user, "role", "UNKNOWN"),
        )
        updated = ManageAdminUseCase(_repo()).update(command)
        return Response(_serialize_admin(updated))


class AdminActivationView(APIView):
    """Activate/deactivate admin endpoints."""

    permission_classes = [CanManageAdminUsers]

    def post(self, request, admin_id: str, action: str):
        manager = ManageAdminUseCase(_repo())
        if action == "activate":
            admin = manager.activate(admin_id)
        elif action == "deactivate":
            admin = manager.deactivate(admin_id)
        else:
            return Response({"detail": "Invalid action"}, status=400)
        return Response(_serialize_admin(admin))
