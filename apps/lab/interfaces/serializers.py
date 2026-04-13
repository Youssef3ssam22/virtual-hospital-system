"""Lab serializers for Specimens, Results, Critical Values, Reports."""
from decimal import Decimal, InvalidOperation

from rest_framework import serializers

from apps.admin.infrastructure.orm_catalog_models import LabCatalogItem
from apps.lab.infrastructure.orm_models import (
    AnalyzerQueue,
    CriticalValue,
    LabReport,
    LabResult,
    RecollectionRequest,
    Specimen,
)
from apps.lab.services import assert_result_transition, assert_specimen_transition


class SpecimenSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(source="order_id", read_only=True)
    patient_id = serializers.UUIDField(source="patient_id", read_only=True)
    encounter_id = serializers.UUIDField(source="encounter_id", read_only=True)

    class Meta:
        model = Specimen
        fields = [
            "id",
            "accession_number",
            "order",
            "order_id",
            "patient",
            "patient_id",
            "encounter",
            "encounter_id",
            "specimen_type",
            "collection_method",
            "collection_time",
            "received_time",
            "quantity",
            "quantity_unit",
            "status",
            "condition",
            "collector_id",
            "rejection_reason",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "received_time", "created_at", "updated_at"]

    def validate(self, data):
        quantity = data.get("quantity", getattr(self.instance, "quantity", None))
        status_value = data.get("status", getattr(self.instance, "status", "ordered"))
        order = data.get("order", getattr(self.instance, "order", None))
        patient = data.get("patient", getattr(self.instance, "patient", None))
        encounter = data.get("encounter", getattr(self.instance, "encounter", None))

        if quantity is not None and quantity <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        if self.instance and status_value != self.instance.status:
            assert_specimen_transition(self.instance, status_value)
        if order and patient and order.patient_id != patient.id:
            raise serializers.ValidationError("Specimen patient must match order patient.")
        if order and encounter and order.encounter_id != encounter.id:
            raise serializers.ValidationError("Specimen encounter must match order encounter.")
        if status_value == "rejected" and not data.get("rejection_reason", getattr(self.instance, "rejection_reason", "")):
            raise serializers.ValidationError("Rejected specimens must include rejection_reason.")
        return data


class RecollectionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecollectionRequest
        fields = ["id", "specimen", "reason", "notes", "status", "requested_at"]
        read_only_fields = ["id", "status", "requested_at"]


class LabResultSerializer(serializers.ModelSerializer):
    specimen_accession = serializers.CharField(source="specimen.accession_number", read_only=True)
    encounter_id = serializers.UUIDField(source="encounter_id", read_only=True)

    class Meta:
        model = LabResult
        fields = [
            "id",
            "order",
            "specimen",
            "specimen_accession",
            "encounter_id",
            "test_code",
            "test_name",
            "result_value",
            "unit",
            "reference_range",
            "reference_range_low",
            "reference_range_high",
            "abnormal",
            "abnormal_flag",
            "status",
            "analyzer_id",
            "reported_by",
            "reported_at",
            "verified_by",
            "verified_at",
            "correction_of",
            "version",
            "notes",
        ]
        read_only_fields = ["id", "reported_at", "verified_by", "verified_at", "version"]

    def validate(self, data):
        low = data.get("reference_range_low")
        high = data.get("reference_range_high")
        test_code = data.get("test_code", getattr(self.instance, "test_code", ""))
        specimen = data.get("specimen", getattr(self.instance, "specimen", None))
        order = data.get("order", getattr(self.instance, "order", None))
        status_value = data.get("status", getattr(self.instance, "status", "pending"))

        if low is not None and high is not None and low > high:
            raise serializers.ValidationError("reference_range_low cannot be greater than reference_range_high.")
        if test_code:
            catalog_item = LabCatalogItem.objects.filter(code__iexact=test_code, is_active=True).first()
            if catalog_item is None:
                raise serializers.ValidationError("test_code must exist in the active lab catalog.")
            data["test_name"] = data.get("test_name") or catalog_item.name
            requested_unit = data.get("unit") or getattr(self.instance, "unit", "") or catalog_item.default_unit
            if catalog_item.default_unit and requested_unit and requested_unit != catalog_item.default_unit:
                raise serializers.ValidationError("unit must match the configured default unit for this lab test.")
            data["unit"] = requested_unit
        if specimen and order and specimen.order_id != order.id:
            raise serializers.ValidationError("Result specimen must belong to the selected order.")
        result_value = data.get("result_value", getattr(self.instance, "result_value", ""))
        if low is not None or high is not None:
            try:
                numeric_value = Decimal(str(result_value))
            except (InvalidOperation, TypeError, ValueError) as exc:
                raise serializers.ValidationError("Numeric result_value is required when reference ranges are numeric.") from exc
            abnormal_flag = data.get("abnormal_flag", getattr(self.instance, "abnormal_flag", "N"))
            if low is not None and numeric_value < low and abnormal_flag not in {"L", "LL"}:
                raise serializers.ValidationError("abnormal_flag must reflect a low result for this reference range.")
            if high is not None and numeric_value > high and abnormal_flag not in {"H", "HH"}:
                raise serializers.ValidationError("abnormal_flag must reflect a high result for this reference range.")
            if low is not None and high is not None and low <= numeric_value <= high and abnormal_flag != "N":
                raise serializers.ValidationError("abnormal_flag must be N when result_value is within range.")
        if self.instance and status_value != self.instance.status:
            assert_result_transition(self.instance, status_value)
        return data


class CriticalValueSerializer(serializers.ModelSerializer):
    test_name = serializers.CharField(source="result.test_name", read_only=True)

    class Meta:
        model = CriticalValue
        fields = [
            "id",
            "result",
            "patient_id",
            "test_name",
            "critical_value",
            "priority",
            "status",
            "reported_to",
            "reported_at",
            "acknowledged_by",
            "acknowledged_at",
            "action_taken",
            "resolution_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LabReportSerializer(serializers.ModelSerializer):
    specimen_accession = serializers.CharField(source="specimen.accession_number", read_only=True)
    patient_id = serializers.UUIDField(source="patient_id", read_only=True)
    encounter_id = serializers.UUIDField(source="encounter_id", read_only=True)
    results_count = serializers.SerializerMethodField()

    class Meta:
        model = LabReport
        fields = [
            "id",
            "order",
            "patient_id",
            "encounter_id",
            "specimen",
            "specimen_accession",
            "status",
            "report_number",
            "generated_at",
            "completed_at",
            "verified_at",
            "released_at",
            "generated_by",
            "verified_by",
            "interpretation",
            "critical_values_count",
            "results_count",
            "attachments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "released_at"]

    def get_results_count(self, obj):
        return obj.order.results.filter(is_active=True).count()

    def validate(self, data):
        order = data.get("order", getattr(self.instance, "order", None))
        specimen = data.get("specimen", getattr(self.instance, "specimen", None))
        if order and specimen and specimen.order_id != order.id:
            raise serializers.ValidationError("Report specimen must belong to the report order.")
        return data


class AnalyzerQueueSerializer(serializers.ModelSerializer):
    specimen_accession = serializers.CharField(source="specimen.accession_number", read_only=True)

    class Meta:
        model = AnalyzerQueue
        fields = [
            "id",
            "specimen",
            "specimen_accession",
            "analyzer_id",
            "priority",
            "status",
            "position_in_queue",
            "queued_at",
            "started_at",
            "completed_at",
            "error_message",
            "retry_count",
            "max_retries",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "position_in_queue", "created_at", "updated_at"]
