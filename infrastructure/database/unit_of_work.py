import logging
from django.db import transaction
from shared.domain.domain_event import DomainEvent

log = logging.getLogger("virtual_hospital.uow")


class UnitOfWork:
    """Collect domain events during a transaction and publish after commit.

    Usage:
        @transaction.atomic
        def execute(self, ...):
            uow = UnitOfWork()
            # ... do DB work ...
            uow.collect(SomethingHappened(...))
            uow.commit()   # schedules publish via on_commit()
    """

    def __init__(self):
        self._events: list[DomainEvent] = []

    def collect(self, event: DomainEvent) -> None:
        self._events.append(event)

    def commit(self) -> None:
        # Snapshot and clear before registering on_commit so that any
        # subsequent collect() + commit() calls in the same use case
        # don't double-publish.
        events_to_publish = list(self._events)
        self._events.clear()

        if not events_to_publish:
            return

        def _publish_all():
            from infrastructure.event_bus.registry import get_event_bus
            bus = get_event_bus()
            for event in events_to_publish:
                try:
                    bus.publish(event)
                except Exception as e:
                    log.error(
                        "Failed to publish event %s after commit: %s",
                        event.event_name, e,
                    )

        # on_commit() fires only when the outermost atomic block commits.
        # If the transaction rolls back, _publish_all is dropped entirely.
        transaction.on_commit(_publish_all)

    # Backward-compatible aliases for any code using the old API
    def collect_event(self, event: DomainEvent) -> None:
        self.collect(event)

    def publish_events(self) -> None:
        self.commit()