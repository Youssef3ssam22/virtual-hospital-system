"""Shared workflow transition guards for production-facing modules."""

from __future__ import annotations


class InvalidTransitionError(ValueError):
    """Raised when a state machine transition is not allowed."""


def ensure_transition(current: str, new: str, transitions: dict[str, set[str]], label: str) -> None:
    current_normalized = (current or "").lower()
    new_normalized = (new or "").lower()
    allowed = transitions.get(current_normalized, set())
    if new_normalized not in allowed:
        allowed_display = ", ".join(sorted(allowed)) or "no transitions"
        raise InvalidTransitionError(
            f"Invalid {label} transition: {current!r} -> {new!r}. Allowed: {allowed_display}."
        )
