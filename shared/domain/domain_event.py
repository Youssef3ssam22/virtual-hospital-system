"""shared/domain/domain_event.py — Base domain event.

Domain events are immutable value objects that represent something that
happened in the domain. They are published to the InMemoryEventBus and
consumed by handlers registered in AppConfig.ready().

All concrete events must be frozen dataclasses that inherit from DomainEvent
and declare their fields with defaults so the event bus can inspect them:

    @dataclass(frozen=True)
    class PrescriptionCreated(DomainEvent):
        prescription_id: str = ""
        patient_id:      str = ""
        encounter_id:    str = ""
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    # Each event gets a unique ID and a precise UTC timestamp at creation time.
    # frozen=True makes the entire event immutable — events must never be modified
    # after they are created, only published and consumed.
    event_id:    UUID     = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def event_name(self) -> str:
        """Returns the class name, used as the lookup key in InMemoryEventBus."""
        return self.__class__.__name__