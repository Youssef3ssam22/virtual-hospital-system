"""shared/domain/exceptions.py — Domain exception hierarchy.

All use cases raise these exceptions. The custom_exception_handler in
shared/utils/exception_handler.py maps them to HTTP status codes.

HTTP mapping:
    EntityNotFound      → 404
    NotFound            → 404
    DuplicateEntity     → 409
    InvalidOperation    → 422
    UnauthorizedOperation → 403
    ConflictOperation   → 409
    ServiceUnavailable  → 503

Usage guide:
    EntityNotFound  — use when looking up by a specific ID that doesn't exist
                      e.g. raise EntityNotFound("Patient", patient_id)
    NotFound        — use for free-form not-found messages without a specific entity
                      e.g. raise NotFound("No open encounter for this patient")
    DuplicateEntity — use when creating something that already exists
                      e.g. raise DuplicateEntity("Staff", employee_number)
    InvalidOperation — use when a domain business rule is violated
                      e.g. raise InvalidOperation("Cannot dispense a rejected prescription")
    ConflictOperation — use when current state prevents the operation
                      e.g. raise ConflictOperation("Encounter is already closed")
    UnauthorizedOperation — use when the actor lacks permission
                      e.g. raise UnauthorizedOperation("Only doctors can create prescriptions")
    ServiceUnavailable — use when an external service (Neo4j, email) is unreachable
                      e.g. raise ServiceUnavailable("CDSS")
"""


class DomainException(Exception):
    """Base class for all domain exceptions."""
    pass


class EntityNotFound(DomainException):
    """A specific entity could not be found by its identifier. → HTTP 404"""
    def __init__(self, entity: str, identifier: str):
        super().__init__(f"{entity} not found: {identifier}")
        self.entity     = entity
        self.identifier = identifier


class NotFound(DomainException):
    """Free-form not-found error without a specific entity type. → HTTP 404
    Use EntityNotFound instead when you have a specific entity and ID.
    """
    def __init__(self, message: str):
        super().__init__(message)


class DuplicateEntity(DomainException):
    """Attempting to create an entity that already exists. → HTTP 409"""
    def __init__(self, entity: str, identifier: str):
        super().__init__(f"{entity} already exists: {identifier}")
        self.entity     = entity
        self.identifier = identifier


class InvalidOperation(DomainException):
    """A domain business rule was violated. → HTTP 422"""
    def __init__(self, message: str):
        super().__init__(message)


class UnauthorizedOperation(DomainException):
    """The actor does not have permission to perform this operation. → HTTP 403"""
    def __init__(self, message: str):
        super().__init__(message)


class ConflictOperation(DomainException):
    """Current entity state prevents this operation. → HTTP 409
    Use DuplicateEntity for creation conflicts, ConflictOperation for state conflicts.
    Example: trying to close an already-closed encounter.
    """
    def __init__(self, message: str):
        super().__init__(message)


class ServiceUnavailable(DomainException):
    """An external dependency (Neo4j, SMTP, etc.) is unreachable. → HTTP 503"""
    def __init__(self, service: str):
        super().__init__(f"{service} is currently unavailable")
        self.service = service