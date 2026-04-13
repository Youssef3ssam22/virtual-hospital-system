"""Lab API views for Specimens, Results, Critical Values, Reports."""
from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.billing.services import auto_create_invoice_item_from_lab_result
from apps.lab.infrastructure.orm_models import (
    AnalyzerQueue,
    CriticalValue,
    LabOrder,
    LabReport,
    LabResult,
    RecollectionRequest,
    Specimen,
)
from apps.lab.interfaces.serializers import (
    AnalyzerQueueSerializer,
    CriticalValueSerializer,
    LabReportSerializer,
    LabResultSerializer,
    RecollectionRequestSerializer,
    SpecimenSerializer,
)
from apps.lab.services import amend_result, finalize_report, transition_specimen, verify_result
from shared.permissions import (
    CanHandleCriticalValues,
    CanManageLabOrders,
    CanManageLabResults,
    CanManageLabSpecimens,
    CanVerifyLabReports,
)
from shared.utils.notifications import emit_event
from shared.utils.state_machines import InvalidTransitionError


class SpecimenViewSet(viewsets.ModelViewSet):
    queryset = Specimen.objects.select_related("order", "patient", "encounter")
    serializer_class = SpecimenSerializer
    permission_classes = [CanManageLabSpecimens]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "specimen_type", "patient", "encounter"]
    search_fields = ["accession_number", "order__id", "patient__mrn", "patient__full_name"]
    ordering_fields = ["collection_time", "received_time"]
    ordering = ["-collection_time"]

    def get_queryset(self):
        return super().get_queryset().filter(archived_at__isnull=True)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        specimen = self.get_object()
        try:
            transition_specimen(specimen, "rejected")
        except InvalidTransitionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        specimen.rejection_reason = request.data.get("reason", "Not specified")
        specimen.save(update_fields=["rejection_reason", "updated_at"])
        return Response(SpecimenSerializer(specimen).data)

    @action(detail=True, methods=["post"])
    def start_processing(self, request, pk=None):
        specimen = self.get_object()
        try:
            transition_specimen(specimen, "processing")
        except InvalidTransitionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(SpecimenSerializer(specimen).data)

    @action(detail=True, methods=["put"])
    def status(self, request, pk=None):
        specimen = self.get_object()
        status_value = request.data.get("status")
        if not status_value:
            return Response({"detail": "status is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            transition_specimen(specimen, status_value)
        except InvalidTransitionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if "condition" in request.data:
            specimen.condition = request.data.get("condition")
            specimen.save(update_fields=["condition", "updated_at"])
        return Response(SpecimenSerializer(specimen).data)

    @action(detail=False, methods=["get"])
    def pending(self, request):
        specimens = self.get_queryset().filter(status__in=["ordered", "collected", "in_transit", "received", "processing"])
        return Response(self.get_serializer(specimens, many=True).data)

    @action(detail=False, methods=["post"])
    def recollect(self, request):
        serializer = RecollectionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_obj = serializer.save()
        return Response(RecollectionRequestSerializer(request_obj).data, status=status.HTTP_201_CREATED)


class LabResultViewSet(viewsets.ModelViewSet):
    queryset = LabResult.objects.select_related("specimen", "order", "encounter")
    serializer_class = LabResultSerializer
    permission_classes = [CanManageLabResults]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "abnormal_flag", "specimen", "encounter"]
    search_fields = ["test_code", "test_name"]
    ordering_fields = ["reported_at", "verified_at"]
    ordering = ["-reported_at"]

    def get_queryset(self):
        return super().get_queryset().filter(archived_at__isnull=True)

    def perform_create(self, serializer):
        order = serializer.validated_data["order"]
        serializer.save(encounter=order.encounter)

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        result = self.get_object()
        try:
            verified = verify_result(result, actor_id=str(request.user.id))
        except InvalidTransitionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        auto_create_invoice_item_from_lab_result(verified, actor_id=str(request.user.id))
        return Response(LabResultSerializer(verified).data)

    @action(detail=True, methods=["post"])
    def amend(self, request, pk=None):
        result = self.get_object()
        try:
            amended = amend_result(
                result,
                new_value=request.data.get("result_value"),
                actor_id=str(request.user.id),
                reason=request.data.get("reason", ""),
            )
        except InvalidTransitionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(LabResultSerializer(amended).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def abnormal(self, request):
        results = self.get_queryset().filter(abnormal_flag__in=["L", "H", "LL", "HH"])
        return Response(self.get_serializer(results, many=True).data)


class CriticalValueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CriticalValue.objects.all()
    serializer_class = CriticalValueSerializer
    permission_classes = [CanHandleCriticalValues]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "priority", "patient_id"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        critical = self.get_object()
        if critical.status == "acknowledged":
            return Response({"detail": "Already acknowledged."}, status=status.HTTP_400_BAD_REQUEST)
        critical.status = "acknowledged"
        critical.acknowledged_by = str(request.user.id)
        critical.acknowledged_at = datetime.utcnow()
        critical.save(update_fields=["status", "acknowledged_by", "acknowledged_at", "updated_at"])
        emit_event("lab_critical", "lab.critical_result", {"critical_value_id": str(critical.id), "status": critical.status})
        return Response(CriticalValueSerializer(critical).data)

    @action(detail=True, methods=["post"])
    def notify(self, request, pk=None):
        critical = self.get_object()
        notified_to = request.data.get("notified_to")
        if not notified_to:
            return Response({"detail": "notified_to required."}, status=status.HTTP_400_BAD_REQUEST)
        critical.reported_to = notified_to
        critical.reported_at = datetime.utcnow()
        critical.save(update_fields=["reported_to", "reported_at", "updated_at"])
        emit_event("lab_critical", "lab.critical_result", {"critical_value_id": str(critical.id), "reported_to": notified_to})
        return Response(CriticalValueSerializer(critical).data)

    @action(detail=False, methods=["get"])
    def unacknowledged(self, request):
        return Response(self.get_serializer(self.get_queryset().filter(status="new"), many=True).data)


class LabReportViewSet(viewsets.ModelViewSet):
    queryset = LabReport.objects.select_related("specimen", "order", "patient", "encounter")
    serializer_class = LabReportSerializer
    permission_classes = [CanVerifyLabReports]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "patient", "encounter"]
    search_fields = ["report_number", "order__id", "patient__mrn", "patient__full_name"]
    ordering_fields = ["generated_at", "verified_at"]
    ordering = ["-generated_at"]

    def get_queryset(self):
        return super().get_queryset().filter(archived_at__isnull=True)

    @action(detail=True, methods=["post"])
    def finalize(self, request, pk=None):
        report = self.get_object()
        try:
            report = finalize_report(report, actor_id=str(request.user.id), release=False)
        except InvalidTransitionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(LabReportSerializer(report).data)

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        report = self.get_object()
        try:
            report = finalize_report(report, actor_id=str(request.user.id), release=False)
        except InvalidTransitionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(LabReportSerializer(report).data)

    @action(detail=True, methods=["post"])
    def release(self, request, pk=None):
        report = self.get_object()
        try:
            report = finalize_report(report, actor_id=str(request.user.id), release=True)
        except InvalidTransitionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(LabReportSerializer(report).data)


class AnalyzerQueueViewSet(viewsets.ModelViewSet):
    queryset = AnalyzerQueue.objects.select_related("specimen")
    serializer_class = AnalyzerQueueSerializer
    permission_classes = [CanManageLabSpecimens]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "priority", "analyzer_id"]
    ordering_fields = ["priority", "position_in_queue", "queued_at"]
    ordering = ["priority", "position_in_queue"]

    @action(detail=True, methods=["put"])
    def status(self, request, pk=None):
        queue_item = self.get_object()
        status_value = request.data.get("status")
        if not status_value:
            return Response({"detail": "status required."}, status=status.HTTP_400_BAD_REQUEST)
        queue_item.status = status_value
        queue_item.save(update_fields=["status", "updated_at"])
        return Response(AnalyzerQueueSerializer(queue_item).data)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        queue_item = self.get_object()
        if queue_item.status != "queued":
            return Response({"detail": "Can only start queued items."}, status=status.HTTP_400_BAD_REQUEST)
        queue_item.mark_processing()
        queue_item.save(update_fields=["status", "started_at", "updated_at"])
        return Response(AnalyzerQueueSerializer(queue_item).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        queue_item = self.get_object()
        if queue_item.status != "processing":
            return Response({"detail": "Can only complete items in processing status."}, status=status.HTTP_400_BAD_REQUEST)
        queue_item.mark_completed()
        queue_item.save(update_fields=["status", "completed_at", "updated_at"])
        try:
            transition_specimen(queue_item.specimen, "analyzed")
        except InvalidTransitionError:
            pass
        return Response(AnalyzerQueueSerializer(queue_item).data)

    @action(detail=True, methods=["post"])
    def fail(self, request, pk=None):
        queue_item = self.get_object()
        queue_item.error_message = request.data.get("error_message", "")
        queue_item.retry_count += 1
        queue_item.status = "retry" if queue_item.retry_count < queue_item.max_retries else "failed"
        queue_item.save(update_fields=["error_message", "retry_count", "status", "updated_at"])
        return Response(AnalyzerQueueSerializer(queue_item).data)


class WorklistView(APIView):
    permission_classes = [CanManageLabOrders]

    def get(self, request):
        queryset = LabOrder.objects.select_related("patient", "encounter").filter(archived_at__isnull=True)
        status_filter = request.query_params.get("status")
        priority = request.query_params.get("priority")
        date_str = request.query_params.get("date")
        if status_filter:
            queryset = queryset.filter(status__iexact=status_filter)
        if priority:
            queryset = queryset.filter(priority__iexact=priority)
        if date_str:
            try:
                date_value = datetime.fromisoformat(date_str).date()
                queryset = queryset.filter(created_at__date=date_value)
            except ValueError:
                return Response({"detail": "Invalid date format. Use ISO 8601."}, status=400)
        data = list(queryset.values("id", "patient_id", "encounter_id", "test_codes", "ordered_by", "status", "priority", "created_at"))
        return Response(data)


class AccessionsViewSet(viewsets.ViewSet):
    permission_classes = [CanManageLabSpecimens]

    def list(self, request):
        specimens = Specimen.objects.exclude(accession_number="").filter(archived_at__isnull=True).order_by("-received_time")
        return Response(SpecimenSerializer(specimens, many=True).data)

    def retrieve(self, request, pk=None):
        specimen = Specimen.objects.get(id=pk)
        return Response(SpecimenSerializer(specimen).data)

    def create(self, request):
        payload = request.data.copy()
        if not payload.get("accession_number"):
            payload["accession_number"] = _generate_accession_number()
        serializer = SpecimenSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        specimen = serializer.save()
        return Response(SpecimenSerializer(specimen).data, status=status.HTTP_201_CREATED)


class PanelViewSet(viewsets.ViewSet):
    permission_classes = [CanManageLabOrders]

    def list(self, request):
        queryset = LabOrder.objects.filter(archived_at__isnull=True)
        status_filter = request.query_params.get("status")
        patient_id = request.query_params.get("patientId")
        if status_filter:
            queryset = queryset.filter(status__iexact=status_filter)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        data = list(queryset.values("id", "patient_id", "encounter_id", "status", "priority", "created_at"))
        return Response(data)

    def retrieve(self, request, pk=None):
        order = LabOrder.objects.get(id=pk)
        results = LabResult.objects.filter(order=order, archived_at__isnull=True)
        return Response({
            "order": {
                "id": str(order.id),
                "patient_id": str(order.patient_id),
                "encounter_id": str(order.encounter_id),
                "status": order.status,
                "priority": order.priority,
                "test_codes": order.test_codes,
            },
            "results": LabResultSerializer(results, many=True).data,
        })

    @action(detail=True, methods=["post"])
    def results(self, request, pk=None):
        order = LabOrder.objects.get(id=pk)
        payload = request.data.copy()
        payload["order"] = str(order.id)
        serializer = LabResultSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        result = serializer.save(encounter=order.encounter)
        return Response(LabResultSerializer(result).data, status=status.HTTP_201_CREATED)


def _generate_accession_number() -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"ACC-{timestamp}"
