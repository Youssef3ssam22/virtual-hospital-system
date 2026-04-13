"""infrastructure/event_bus/registry.py — Event bus registry.

The registry owns the single process-wide InMemoryEventBus instance.
All production code should import get_event_bus() from here.
Tests reset the bus between cases using reset_event_bus().

Usage (production):
    from infrastructure.event_bus.registry import get_event_bus
    get_event_bus().publish(SomethingHappened(...))
    get_event_bus().subscribe(SomethingHappened, my_handler)

Usage (tests — in conftest.py):
    @pytest.fixture(autouse=True)
    def clean_event_bus():
        reset_event_bus()
        yield
        reset_event_bus()

Architecture note:
    Each Celery worker is a separate OS process with its own _bus instance.
    Workers do NOT share the event bus — they communicate via the Celery task
    queue (Redis). AppConfig.ready() subscriptions run in each process separately,
    so each worker has its own subscriptions. This is correct and intentional.
"""
from infrastructure.event_bus.in_memory_bus import InMemoryEventBus

_bus: InMemoryEventBus | None = None


def get_event_bus() -> InMemoryEventBus:
    """Return the process-wide event bus, creating it on first call."""
    global _bus
    if _bus is None:
        _bus = InMemoryEventBus()
    return _bus


def reset_event_bus() -> None:
    """Replace the current bus with a fresh empty instance.

    All subscriptions registered via AppConfig.ready() are lost after this call.
    This is intentional in tests (clean slate between cases).
    Never call this in production code.
    """
    global _bus
    _bus = InMemoryEventBus()