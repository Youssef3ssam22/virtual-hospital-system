"""infrastructure/event_bus/in_memory_bus.py — Synchronous in-process event bus."""
import logging
from collections import defaultdict
from typing import Callable, Type
from shared.domain.domain_event import DomainEvent

logger = logging.getLogger("virtual_hospital.event_bus")


class InMemoryEventBus:
    def __init__(self):
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        """Register a handler for an event type.

        The key is the event class name string so handlers survive across
        import reloads in development (where classes can be re-imported).
        """
        self._handlers[event_type.__name__].append(handler)
        logger.debug("Subscribed %s to %s", handler.__qualname__, event_type.__name__)

    def publish(self, event: DomainEvent) -> None:
        """Deliver an event to all registered handlers.

        Handlers are called synchronously in subscription order.
        A failing handler is logged and skipped — it does not prevent
        subsequent handlers from receiving the event.
        """
        handlers = self._handlers.get(event.event_name, [])
        if not handlers:
            logger.debug("No handlers registered for %s", event.event_name)
            return
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(
                    "Handler %s failed for event %s: %s",
                    handler.__qualname__, event.event_name, e,
                )

# NOTE: do NOT use this module-level instance directly.
# Always use infrastructure.event_bus.registry.get_event_bus() which returns
# the managed singleton. Importing event_bus from here gives you a DIFFERENT
# instance that has no subscriptions — a silent split-brain bug.
# This instance exists only for backward compatibility and will be removed.
# _event_bus_DO_NOT_USE = InMemoryEventBus()