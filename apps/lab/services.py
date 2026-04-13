"""Laboratory workflow guards and automation."""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.lab.infrastructure.orm_models import CriticalValue, LabReport, LabResult, Specimen
from shared.utils.notifications import emit_event
from shared.utils.state_machines import InvalidTransitionError, ensure_transition


SPECIMEN_TRANSITIONS = {
    "ordered": {"collected", "rejected"},
    "collected": {"in_transit", "rejected"},
    "in_transit": {"received", "rejected"},
    "received": {"processing", "rejected"},
    "processing": {"analyzed", "rejected"},
    "analyzed": {"resulted"},
    "resulted": set(),
    "rejected": set(),
    "archived": set(),
}

LAB_RESULT_TRANSITIONS = {
    "pending": {"preliminary", "completed", "cancelled"},
    "preliminary": {"completed", "verified", "cancelled"},
    "completed": {"verified", "amended", "cancelled"},
    "verified": {"amended"},
    "amended": {"verified"},
    "cancelled": set(),
}

LAB_REPORT_TRANSITIONS = {
    "draft": {"preliminary", "final", "cancelled"},
    "preliminary": {"final", "corrected", "cancelled"},
    "final": {"corrected"},
    "corrected": {"final"},
    "cancelled": set(),
}


def assert_specimen_transition(specimen: Specimen, new_status: str) -> None:
    ensure_transition(specimen.status, new_status, SPECIMEN_TRANSITIONS, "specimen")


@transaction.atomic
def transition_specimen(specimen: Specimen, new_status: str) -> Specimen:
    specimen = Specimen.objects.select_for_update().get(pk=specimen.pk)
    assert_specimen_transition(specimen, new_status)
    specimen.status = new_status
    if new_status == "received" and specimen.received_time is None:
        specimen.received_time = timezone.now()
    specimen.save(update_fields=["status", "received_time", "updated_at"])
    return specimen


def assert_result_transition(result: LabResult, new_status: str) -> None:
    ensure_transition(result.status, new_status, LAB_RESULT_TRANSITIONS, "lab result")
    if new_status == "verified":
        if not result.specimen_id or result.specimen.status != "analyzed":
            raise InvalidTransitionError("Cannot verify result before specimen reaches analyzed status.")
        if not result.result_value:
            raise InvalidTransitionError("Cannot verify result without a value.")
    if result.status == "verified" and new_status not in {"amended"}:
        raise InvalidTransitionError("Verified results are immutable except through amendment.")


@transaction.atomic
def verify_result(result: LabResult, actor_id: str) -> LabResult:
    result = LabResult.objects.select_for_update().select_related("specimen", "order", "encounter").get(pk=result.pk)
    assert_result_transition(result, "verified")
    result.status = "verified"
    result.verified_by = actor_id
    result.verified_at = timezone.now()
    result.save(update_fields=["status", "verified_by", "verified_at"])
    if result.abnormal_flag in {"LL", "HH"}:
        critical_value, _ = CriticalValue.objects.get_or_create(
            result=result,
            defaults={
                "patient_id": str(result.order.patient_id),
                "test_name": result.test_name,
                "critical_value": str(result.result_value),
                "priority": "high",
            },
        )
        emit_event(
            "lab_critical",
            "lab.critical_result",
            {
                "critical_value_id": str(critical_value.id),
                "result_id": str(result.id),
                "patient_id": str(result.order.patient_id),
                "encounter_id": str(result.encounter_id),
                "test_name": result.test_name,
                "critical_value": str(result.result_value),
            },
        )
    return result


@transaction.atomic
def amend_result(result: LabResult, new_value: str, actor_id: str, reason: str = "") -> LabResult:
    result = LabResult.objects.select_for_update().select_related("order", "specimen", "encounter").get(pk=result.pk)
    if result.status not in {"verified", "completed"}:
        raise InvalidTransitionError("Only completed or verified results can be amended.")
    LabResult.objects.filter(id=result.id).update(is_active=False)
    amended = LabResult.objects.create(
        order=result.order,
        specimen=result.specimen,
        encounter=result.encounter,
        test_code=result.test_code,
        test_name=result.test_name,
        result_value=new_value,
        unit=result.unit,
        reference_range=result.reference_range,
        reference_range_low=result.reference_range_low,
        reference_range_high=result.reference_range_high,
        abnormal=result.abnormal,
        abnormal_flag=result.abnormal_flag,
        status="amended",
        analyzer_id=result.analyzer_id,
        reported_by=actor_id,
        correction_of=result,
        version=result.version + 1,
        notes=reason or result.notes,
    )
    return amended


@transaction.atomic
def finalize_report(report: LabReport, actor_id: str, release: bool = False) -> LabReport:
    report = LabReport.objects.select_for_update().select_related("order", "patient", "encounter").get(pk=report.pk)
    ensure_transition(report.status, "final", LAB_REPORT_TRANSITIONS, "lab report")
    order_results = report.order.results.filter(is_active=True)
    if order_results.exclude(status="verified").exists():
        raise InvalidTransitionError("All results must be verified before a report can be finalized.")
    report.status = "final"
    report.completed_at = timezone.now()
    report.verified_at = report.verified_at or timezone.now()
    report.verified_by = report.verified_by or actor_id
    if release:
        report.released_at = timezone.now()
        emit_event(
            "lab_reports",
            "lab.report_ready",
            {
                "report_id": str(report.id),
                "order_id": str(report.order_id),
                "patient_id": str(report.patient_id),
                "encounter_id": str(report.encounter_id),
            },
        )
    report.save(update_fields=["status", "completed_at", "verified_at", "verified_by", "released_at", "updated_at"])
    return report
