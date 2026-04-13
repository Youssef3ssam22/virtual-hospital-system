"""Idempotency helpers and middleware for critical POST endpoints."""

from __future__ import annotations

import hashlib
import json

from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.utils import timezone

from apps.auth.infrastructure.orm_models import AuthToken
from shared.models import IdempotencyRecord


CRITICAL_POST_PREFIXES = (
    "/api/v1/billing/payments",
    "/api/v1/billing/claims",
    "/api/v1/billing/insurance-claims",
    "/api/v1/billing/invoices",
    "/api/v1/lab/results",
)


def resolve_actor_id(request) -> str:
    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False) and getattr(user, "id", None):
        return str(user.id)

    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
    if auth_header.startswith("Bearer "):
        access_token = auth_header.replace("Bearer ", "", 1).strip()
        if access_token:
            token = AuthToken.objects.filter(access_token=access_token, is_valid=True).only("user_id").first()
            if token:
                return str(token.user_id)
    return "anonymous"


def is_idempotent_endpoint(request) -> bool:
    if request.method != "POST":
        return False
    if request.path.startswith("/api/v1/lab/panels/") and request.path.endswith("/results"):
        return True
    return any(request.path.startswith(prefix) for prefix in CRITICAL_POST_PREFIXES)


def build_request_hash(request, actor_id: str) -> str:
    raw_body = request.body or b""
    digest = hashlib.sha256()
    digest.update(actor_id.encode("utf-8"))
    digest.update(request.method.encode("utf-8"))
    digest.update(request.path.encode("utf-8"))
    digest.update(raw_body)
    return digest.hexdigest()


def serialize_response_body(response):
    if hasattr(response, "data"):
        return json.loads(json.dumps(response.data, default=str))
    content = getattr(response, "content", b"")
    if not content:
        return {}
    try:
        return json.loads(content.decode("utf-8"))
    except Exception:
        return {"raw": content.decode("utf-8", errors="replace")}


class IdempotencyMiddleware:
    """Prevents duplicate execution of critical POST endpoints."""

    HEADER_NAME = "HTTP_IDEMPOTENCY_KEY"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not is_idempotent_endpoint(request):
            return self.get_response(request)

        idempotency_key = request.META.get(self.HEADER_NAME)
        if not idempotency_key:
            return self.get_response(request)

        actor_id = resolve_actor_id(request)
        request_hash = build_request_hash(request, actor_id=actor_id)

        try:
            with transaction.atomic():
                record, created = IdempotencyRecord.objects.select_for_update().get_or_create(
                    actor_id=actor_id,
                    key=idempotency_key,
                    method=request.method,
                    path=request.path,
                    defaults={"request_hash": request_hash, "status": "processing"},
                )
        except IntegrityError:
            record = IdempotencyRecord.objects.get(
                actor_id=actor_id,
                key=idempotency_key,
                method=request.method,
                path=request.path,
            )
            created = False

        if not created:
            if record.request_hash != request_hash:
                return JsonResponse(
                    {"detail": "Idempotency-Key already used for a different request payload."},
                    status=409,
                )
            if record.status == "completed":
                return JsonResponse(record.response_body, status=record.response_code or 200, safe=False)
            if record.status == "failed":
                return JsonResponse(record.response_body, status=record.response_code or 409, safe=False)
            return JsonResponse(
                {"detail": "A request with this Idempotency-Key is already being processed."},
                status=409,
            )

        request._idempotency_record_id = str(record.id)
        response = self.get_response(request)

        response_body = serialize_response_body(response)
        update_values = {
            "status": "completed" if 200 <= response.status_code < 500 else "failed",
            "response_code": response.status_code,
            "response_body": response_body,
            "processed_at": timezone.now(),
            "updated_at": timezone.now(),
        }
        IdempotencyRecord.objects.filter(id=record.id).update(**update_values)
        return response
