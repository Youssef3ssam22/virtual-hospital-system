"""HTTP handlers for lab APIs."""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.admin.infrastructure.orm_catalog_models import LabCatalogItem
from apps.lab.application.use_cases.get_lab import GetLabUseCase
from apps.lab.application.use_cases.register_lab import CreateLabOrderCommand, RegisterLabUseCase
from apps.lab.infrastructure.repositories import DjangoLabOrderRepository
from shared.permissions import CanManageLabOrders
from shared.domain.exceptions import EntityNotFound


def _repo() -> DjangoLabOrderRepository:
    return DjangoLabOrderRepository()


def _serialize_order(order) -> dict:
    return {
        "id": order.id,
        "patient_id": str(order.patient_id),
        "encounter_id": str(order.encounter_id),
        "test_codes": order.test_codes,
        "ordered_by": order.ordered_by,
        "status": str(order.status),
        "priority": order.priority,
        "is_active": order.is_active,
    }


class LabOrderListCreateView(APIView):
    permission_classes = [CanManageLabOrders]

    def get(self, request):
        patient_id = request.query_params.get("patient_id")
        if patient_id:
            orders = GetLabUseCase(_repo()).orders_for_patient(patient_id)
        else:
            orders = GetLabUseCase(_repo()).pending_orders()
        return Response([_serialize_order(o) for o in orders])

    def post(self, request):
        test_codes = [str(code).upper() for code in request.data.get("test_codes", [])]
        if not test_codes:
            return Response({"detail": "test_codes is required."}, status=status.HTTP_400_BAD_REQUEST)
        valid_codes = set(LabCatalogItem.objects.filter(code__in=test_codes, is_active=True).values_list("code", flat=True))
        missing_codes = [code for code in test_codes if code not in valid_codes]
        if missing_codes:
            return Response({"detail": f"Unknown or inactive lab catalog codes: {', '.join(missing_codes)}"}, status=status.HTTP_400_BAD_REQUEST)

        command = CreateLabOrderCommand(
            patient_id=request.data.get("patient_id"),
            encounter_id=request.data.get("encounter_id"),
            test_codes=test_codes,
            ordered_by=request.data.get("ordered_by", str(request.user.id)),
            priority=request.data.get("priority", "ROUTINE"),
            notes=request.data.get("notes"),
            actor_id=str(request.user.id),
            actor_role=getattr(request.user, "role", "UNKNOWN"),
        )
        try:
            created = RegisterLabUseCase(_repo()).execute(command)
        except (ValueError, EntityNotFound) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(_serialize_order(created), status=status.HTTP_201_CREATED)


class LabOrderDetailView(APIView):
    permission_classes = [CanManageLabOrders]

    def get(self, request, order_id: str):
        order = GetLabUseCase(_repo()).order_by_id(order_id)
        return Response(_serialize_order(order))
