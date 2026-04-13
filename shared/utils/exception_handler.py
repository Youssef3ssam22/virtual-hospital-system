"""shared/utils/exception_handler.py — Custom DRF exception handler.

Registered in settings.py:
    REST_FRAMEWORK = {
        "EXCEPTION_HANDLER": "shared.utils.exception_handler.custom_exception_handler",
    }

Maps domain exceptions to consistent JSON error responses.
All error responses follow this shape:
    {"error": true, "code": "ERROR_CODE", "message": "Human-readable message"}
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from shared.domain.exceptions import (
    EntityNotFound, NotFound, DuplicateEntity,
    InvalidOperation, UnauthorizedOperation,
    ConflictOperation, ServiceUnavailable, DomainException,
)

log = logging.getLogger("virtual_hospital")

# Maps exception class → (HTTP status code, error code string)
# ORDER MATTERS: more specific classes must come before their parents.
# EntityNotFound, NotFound, DuplicateEntity etc. all inherit from DomainException.
# If DomainException were listed first, it would match before the specific classes.
_EXCEPTION_MAP: dict = {
    EntityNotFound:        (status.HTTP_404_NOT_FOUND,            "ENTITY_NOT_FOUND"),
    NotFound:              (status.HTTP_404_NOT_FOUND,            "NOT_FOUND"),
    DuplicateEntity:       (status.HTTP_409_CONFLICT,             "DUPLICATE_ENTITY"),
    InvalidOperation:      (status.HTTP_422_UNPROCESSABLE_ENTITY, "INVALID_OPERATION"),
    UnauthorizedOperation: (status.HTTP_403_FORBIDDEN,            "FORBIDDEN"),
    ConflictOperation:     (status.HTTP_409_CONFLICT,             "CONFLICT"),
    ServiceUnavailable:    (status.HTTP_503_SERVICE_UNAVAILABLE,  "SERVICE_UNAVAILABLE"),
    DomainException:       (status.HTTP_422_UNPROCESSABLE_ENTITY, "DOMAIN_ERROR"),
}


def custom_exception_handler(exc, context):
    # Let DRF handle its own exceptions first (AuthenticationFailed,
    # PermissionDenied, ValidationError, NotAuthenticated, etc.)
    response = exception_handler(exc, context)

    # Map domain exceptions to HTTP responses
    for exc_class, (http_status, code) in _EXCEPTION_MAP.items():
        if isinstance(exc, exc_class):
            return Response(
                {"error": True, "code": code, "message": str(exc)},
                status=http_status,
            )

    # If DRF already produced a response (e.g. 401, 400) return it as-is
    if response is not None:
        return response

    # Completely unhandled exception → 500
    # Log with full traceback so we can diagnose in production
    log.exception(
        "Unhandled exception in %s: %s",
        context.get("view").__class__.__name__ if context.get("view") else "unknown view",
        exc,
    )
    return Response(
        {"error": True, "code": "INTERNAL_ERROR", "message": "An unexpected error occurred. Please try again."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )