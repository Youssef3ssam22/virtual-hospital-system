"""Admin API views for Department, Ward, Bed, and BedAssignment management."""
from django.db import models, transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.admin.infrastructure.orm_admin_models import Bed, BedAssignment, Department, Ward
from apps.admin.interfaces.serializers import BedAssignmentSerializer, BedSerializer, DepartmentSerializer, WardSerializer
from apps.billing.services import auto_create_invoice_item_from_bed_assignment
from shared.permissions import CanManageBeds, CanManageDepartments, CanManageWards


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [CanManageDepartments]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "department_type", "is_clinical"]
    search_fields = ["name", "code", "description", "manager_name", "location"]
    ordering_fields = ["name", "created_at", "department_type"]
    ordering = ["name"]

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        department = self.get_object()
        department.status = "active"
        department.save(update_fields=["status", "updated_at"])
        return Response(DepartmentSerializer(department).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        department = self.get_object()
        if department.ward_set.filter(status="active").exists():
            return Response({"detail": "Cannot deactivate department with active wards."}, status=status.HTTP_400_BAD_REQUEST)
        department.status = "inactive"
        department.save(update_fields=["status", "updated_at"])
        return Response(DepartmentSerializer(department).data)

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        department = self.get_object()
        wards = department.ward_set.all()
        total_beds = Bed.objects.filter(ward__department=department).count()
        occupied_beds = BedAssignment.objects.filter(bed__ward__department=department, status="active", archived_at__isnull=True).count()
        return Response({
            "department_id": str(department.id),
            "name": department.name,
            "department_type": department.department_type,
            "total_wards": wards.count(),
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "available_beds": max(total_beds - occupied_beds, 0),
            "occupancy_rate": (occupied_beds / total_beds * 100) if total_beds > 0 else 0,
        })


class WardViewSet(viewsets.ModelViewSet):
    queryset = Ward.objects.select_related("department")
    serializer_class = WardSerializer
    permission_classes = [CanManageWards]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["department", "status", "type", "gender_restriction", "age_group", "supports_isolation"]
    search_fields = ["name", "code", "specialty", "nurse_station"]
    ordering_fields = ["name", "type", "created_at", "total_beds"]
    ordering = ["name"]

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        ward = self.get_object()
        ward.status = "active"
        ward.save(update_fields=["status", "updated_at"])
        return Response(WardSerializer(ward).data)

    @action(detail=True, methods=["post"])
    def maintenance(self, request, pk=None):
        ward = self.get_object()
        if BedAssignment.objects.filter(bed__ward=ward, status="active", archived_at__isnull=True).exists():
            return Response({"detail": "Cannot put ward under maintenance with occupied beds."}, status=status.HTTP_400_BAD_REQUEST)
        ward.status = "maintenance"
        ward.save(update_fields=["status", "updated_at"])
        return Response(WardSerializer(ward).data)

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        ward = self.get_object()
        beds = ward.beds.all()
        occupied = BedAssignment.objects.filter(bed__ward=ward, status="active", archived_at__isnull=True).count()
        available = max(beds.count() - occupied, 0)
        return Response({
            "ward_id": str(ward.id),
            "name": ward.name,
            "type": ward.type,
            "gender_restriction": ward.gender_restriction,
            "age_group": ward.age_group,
            "total_beds": ward.total_beds,
            "occupied_beds": occupied,
            "available_beds": available,
            "occupied_by_type": {
                item["type"]: item["count"]
                for item in beds.filter(status="occupied").values("type").annotate(count=models.Count("id"))
            },
        })


class BedViewSet(viewsets.ModelViewSet):
    queryset = Bed.objects.select_related("ward", "ward__department")
    serializer_class = BedSerializer
    permission_classes = [CanManageBeds]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["ward", "status", "type", "bed_class", "cleaning_status"]
    search_fields = ["bed_number", "room_number", "patient_id"]
    ordering_fields = ["bed_number", "room_number", "type", "status"]
    ordering = ["bed_number"]

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def occupy(self, request, pk=None):
        bed = Bed.objects.select_for_update().select_related("ward", "ward__department").get(pk=self.get_object().pk)
        if bed.assignments.select_for_update().filter(status__in=["reserved", "active"], archived_at__isnull=True).exists():
            return Response({"detail": "Bed is already assigned."}, status=status.HTTP_409_CONFLICT)
        serializer = BedAssignmentSerializer(data={
            "patient": request.data.get("patient"),
            "encounter": request.data.get("encounter"),
            "bed": str(bed.id),
            "start_time": request.data.get("start_time") or timezone.now(),
            "status": "active",
            "assigned_by": str(request.user.id),
            "notes": request.data.get("notes", ""),
        })
        serializer.is_valid(raise_exception=True)
        assignment = serializer.save()
        bed.cleaning_status = "clean"
        bed.blocked_reason = ""
        bed.save()
        self._sync_ward_capacity(bed.ward)
        return Response({"bed": BedSerializer(bed).data, "assignment": BedAssignmentSerializer(assignment).data})

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def release(self, request, pk=None):
        bed = Bed.objects.select_for_update().select_related("ward", "ward__department").get(pk=self.get_object().pk)
        assignment = bed.assignments.select_for_update().filter(status="active", archived_at__isnull=True).order_by("-start_time").first()
        if assignment is None:
            return Response({"detail": "No active bed assignment found."}, status=status.HTTP_400_BAD_REQUEST)
        assignment.status = "completed"
        assignment.end_time = timezone.now()
        assignment.save(update_fields=["status", "end_time", "updated_at"])
        bed.cleaning_status = "needs_cleaning"
        bed.save()
        auto_create_invoice_item_from_bed_assignment(assignment, actor_id=str(request.user.id))
        self._sync_ward_capacity(bed.ward)
        return Response({"bed": BedSerializer(bed).data, "assignment": BedAssignmentSerializer(assignment).data})

    @action(detail=True, methods=["post"])
    def mark_clean(self, request, pk=None):
        bed = self.get_object()
        bed.cleaning_status = "clean"
        bed.blocked_reason = ""
        bed.save(update_fields=["cleaning_status", "blocked_reason", "updated_at"])
        self._sync_ward_capacity(bed.ward)
        return Response(BedSerializer(bed).data)

    @action(detail=True, methods=["post"])
    def maintenance(self, request, pk=None):
        bed = self.get_object()
        if bed.assignments.filter(status="active", archived_at__isnull=True).exists():
            return Response({"detail": "Cannot put occupied bed under maintenance."}, status=status.HTTP_400_BAD_REQUEST)
        bed.status = "maintenance"
        bed.cleaning_status = "cleaning_in_progress"
        bed.save(update_fields=["status", "cleaning_status", "updated_at"])
        self._sync_ward_capacity(bed.ward)
        return Response(BedSerializer(bed).data)

    @action(detail=True, methods=["post"])
    def block(self, request, pk=None):
        bed = self.get_object()
        if bed.assignments.filter(status="active", archived_at__isnull=True).exists():
            return Response({"detail": "Cannot block an occupied bed."}, status=status.HTTP_400_BAD_REQUEST)
        blocked_reason = request.data.get("blocked_reason")
        if not blocked_reason:
            return Response({"detail": "blocked_reason is required."}, status=status.HTTP_400_BAD_REQUEST)
        bed.blocked_reason = blocked_reason
        bed.save(update_fields=["blocked_reason", "updated_at"])
        self._sync_ward_capacity(bed.ward)
        return Response(BedSerializer(bed).data)

    @staticmethod
    def _sync_ward_capacity(ward: Ward):
        total_beds = ward.beds.count()
        active_assignments = BedAssignment.objects.filter(bed__ward=ward, status__in=["reserved", "active"], archived_at__isnull=True).count()
        ward.total_beds = total_beds
        ward.available_beds = max(total_beds - active_assignments, 0)
        ward.save(update_fields=["total_beds", "available_beds", "updated_at"])


class BedAssignmentViewSet(viewsets.ModelViewSet):
    queryset = BedAssignment.objects.select_related("patient", "encounter", "bed", "bed__ward")
    serializer_class = BedAssignmentSerializer
    permission_classes = [CanManageBeds]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "bed", "patient", "encounter"]
    ordering_fields = ["start_time", "created_at"]
    ordering = ["-start_time"]

    def get_queryset(self):
        return super().get_queryset().filter(archived_at__isnull=True)

    def perform_destroy(self, instance):
        instance.archived_at = timezone.now()
        instance.status = "cancelled"
        instance.save(update_fields=["archived_at", "status", "updated_at"])
