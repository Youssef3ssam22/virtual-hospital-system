"""infrastructure/audit/audit_logger.py — Audit logging."""
import logging
from django.db import models
from django.utils import timezone
from shared.utils.idempotency import resolve_actor_id

log = logging.getLogger("virtual_hospital.audit")


class AuditAction:
    PATIENT_REGISTERED       = "PATIENT_REGISTERED"
    PATIENT_UPDATED          = "PATIENT_UPDATED"
    PATIENT_DEACTIVATED      = "PATIENT_DEACTIVATED"
    PATIENT_ACTIVATED        = "PATIENT_ACTIVATED"
    PATIENT_VIEWED           = "PATIENT_VIEWED"
    PATIENT_SUMMARY_VIEWED   = "PATIENT_SUMMARY_VIEWED"
    ALLERGY_ADDED            = "ALLERGY_ADDED"
    ALLERGY_REMOVED          = "ALLERGY_REMOVED"
    ENCOUNTER_OPENED         = "ENCOUNTER_OPENED"
    ENCOUNTER_CLOSED         = "ENCOUNTER_CLOSED"
    ENCOUNTER_DISCHARGED     = "ENCOUNTER_DISCHARGED"
    BED_ASSIGNED             = "BED_ASSIGNED"
    LAB_ORDER_CREATED        = "LAB_ORDER_CREATED"
    LAB_SPECIMEN_COLLECTED   = "LAB_SPECIMEN_COLLECTED"
    LAB_RESULTS_ENTERED      = "LAB_RESULTS_ENTERED"
    LAB_ORDER_VERIFIED       = "LAB_ORDER_VERIFIED"
    LAB_ORDER_PUBLISHED      = "LAB_ORDER_PUBLISHED"
    PRESCRIPTION_CREATED     = "PRESCRIPTION_CREATED"
    PRESCRIPTION_VERIFIED    = "PRESCRIPTION_VERIFIED"
    PRESCRIPTION_DISPENSED   = "PRESCRIPTION_DISPENSED"
    PRESCRIPTION_REJECTED    = "PRESCRIPTION_REJECTED"
    IMAGING_ORDER_CREATED    = "IMAGING_ORDER_CREATED"
    IMAGING_SCHEDULED        = "IMAGING_SCHEDULED"
    IMAGING_PERFORMED        = "IMAGING_PERFORMED"
    IMAGING_REPORTED         = "IMAGING_REPORTED"
    NOTE_CREATED             = "NOTE_CREATED"
    NOTE_UPDATED             = "NOTE_UPDATED"
    NOTE_SIGNED              = "NOTE_SIGNED"
    STAFF_CREATED            = "STAFF_CREATED"
    STAFF_UPDATED            = "STAFF_UPDATED"
    STAFF_DEACTIVATED        = "STAFF_DEACTIVATED"
    STAFF_ACTIVATED          = "STAFF_ACTIVATED"
    DEPARTMENT_CREATED       = "DEPARTMENT_CREATED"
    LOGIN                    = "LOGIN"
    LOGIN_FAILED             = "LOGIN_FAILED"
    LOGOUT                   = "LOGOUT"
    PASSWORD_RESET_REQUESTED = "PASSWORD_RESET_REQUESTED"
    PASSWORD_RESET_COMPLETED = "PASSWORD_RESET_COMPLETED"
    CHANGE_PASSWORD          = "CHANGE_PASSWORD"
    NURSING_ASSESSMENT_CREATED = "NURSING_ASSESSMENT_CREATED"
    CARE_PLAN_CREATED          = "CARE_PLAN_CREATED"
    CARE_PLAN_UPDATED          = "CARE_PLAN_UPDATED"
    NURSING_TASK_CREATED       = "NURSING_TASK_CREATED"
    NURSING_TASK_COMPLETED     = "NURSING_TASK_COMPLETED"
    NURSING_TASK_SKIPPED       = "NURSING_TASK_SKIPPED"
    SHIFT_HANDOVER_CREATED     = "SHIFT_HANDOVER_CREATED"
    ADMISSION_CREATED          = "ADMISSION_CREATED"
    PATIENT_DISCHARGED         = "PATIENT_DISCHARGED"
    WARD_ROUND_CREATED         = "WARD_ROUND_CREATED"


class AuditLog(models.Model):
    actor_id    = models.CharField(max_length=50)
    actor_role  = models.CharField(max_length=50)
    action      = models.CharField(max_length=100, db_index=True)
    source_module = models.CharField(max_length=100, blank=True, default="")
    entity_type = models.CharField(max_length=100)
    entity_id   = models.CharField(max_length=500)
    detail      = models.JSONField(null=True, blank=True)
    reason      = models.TextField(blank=True)
    outcome     = models.CharField(max_length=20, blank=True, default="info")
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    occurred_at = models.DateTimeField(db_index=True)

    class Meta:
        app_label = "authentication"
        db_table  = "audit_logs"
        ordering  = ["-occurred_at"]
        indexes   = [
            models.Index(fields=["actor_id"],                 name="ix_audit_actor_id"),
            models.Index(fields=["entity_type", "entity_id"], name="ix_audit_entity"),
        ]

    def __str__(self):
        return f"{self.action} by {self.actor_id} on {self.entity_type}:{self.entity_id}"


class AuditLogger:
    def log(self, actor_id: str, actor_role: str, action: str,
            entity_type: str, entity_id: str,
            detail: dict = None, ip_address: str = None,
            source_module: str = "", reason: str = "",
            outcome: str = "success") -> None:
        # FIX: use transaction.on_commit() so the audit record is written to the
        # DB only AFTER the surrounding transaction commits successfully.
        # Previously, if a use case called audit.log() inside transaction.atomic()
        # and the transaction was later rolled back (e.g. a validation error after
        # the audit call), the audit row was rolled back too — the failed attempt
        # disappeared from the audit trail. For a hospital, you NEED to know about
        # failed operations (blocked prescriptions, failed logins, etc.).
        # on_commit() writes the record in a separate connection after the outer
        # transaction finishes, so it survives even if the main transaction rolls back.
        # NOTE: in CELERY_TASK_ALWAYS_EAGER (dev/test) mode, on_commit fires
        # synchronously at the end of the atomic block — same behaviour as before.
        from django.db import connection, transaction

        def _write():
            try:
                AuditLog.objects.create(
                    actor_id=actor_id,
                    actor_role=actor_role,
                    action=action,
                    source_module=source_module,
                    entity_type=entity_type,
                    entity_id=str(entity_id)[:500],
                    detail=detail,
                    reason=reason,
                    outcome=outcome,
                    ip_address=ip_address,
                    occurred_at=timezone.now(),
                )
            except Exception as exc:
                # Never let audit logging crash the application
                log.error("AuditLogger.log failed: %s", exc)

        # If we're inside an active transaction, defer to after commit.
        # If we're not inside a transaction (e.g. called from a Celery task),
        # execute immediately — on_commit is a no-op outside atomic blocks.
        try:
            transaction.on_commit(_write)
        except Exception:
            # Fallback: write immediately if on_commit is unavailable
            _write()

        log.debug("[AUDIT] %s by %s (%s) on %s:%s",
                  action, actor_id, actor_role, entity_type, entity_id)


class AuditMiddleware:
    """Captures HTTP method and path for every authenticated write request.

    NOTE: use cases already log specific clinical actions (PRESCRIPTION_CREATED,
    LAB_ORDER_CREATED, etc.). This middleware only logs the raw HTTP request as a
    last-resort catch for any endpoint that doesn't have use-case-level audit logging
    (e.g. Django admin actions, third-party endpoint calls).
    It does NOT duplicate use-case logs — the use cases log WHAT happened clinically,
    the middleware logs that an HTTP request was made. Both serve different purposes.
    """

    WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})

    # Paths whose use-cases already produce specific audit actions.
    # Middleware logging for these is redundant so we skip it.
    SKIP_PREFIXES = (
        "/api/v1/auth/login",
        "/api/v1/auth/logout",
        "/api/v1/auth/change-password",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.method in self.WRITE_METHODS and not any(request.path.startswith(p) for p in self.SKIP_PREFIXES):
            try:
                actor_id = resolve_actor_id(request)
                actor_role = getattr(request.user, "role", "ANONYMOUS") if getattr(request, "user", None) and getattr(request.user, "is_authenticated", False) else "ANONYMOUS"
                AuditLog.objects.create(
                    actor_id=actor_id,
                    actor_role=actor_role,
                    action=f"HTTP_{request.method}",
                    source_module="http",
                    entity_type="Request",
                    entity_id=request.path[:500],
                    detail={
                        "path":   request.path,
                        "method": request.method,
                        "status": response.status_code,
                        "idempotency_key": request.META.get("HTTP_IDEMPOTENCY_KEY", ""),
                    },
                    outcome="success" if 200 <= response.status_code < 300 else "failure",
                    ip_address=request.META.get("REMOTE_ADDR"),
                    occurred_at=timezone.now(),
                )
            except Exception:
                pass

        return response
