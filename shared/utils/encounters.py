"""Encounter lifecycle guards shared across modules."""

from __future__ import annotations

from shared.utils.state_machines import ensure_transition


ENCOUNTER_TRANSITIONS = {
    "planned": {"active", "cancelled"},
    "active": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}


def assert_encounter_transition(encounter, new_status: str) -> None:
    ensure_transition(encounter.status, new_status, ENCOUNTER_TRANSITIONS, "encounter")


def ensure_encounter_allows_orders(encounter) -> None:
    if encounter.status in {"completed", "cancelled"}:
        raise ValueError("Cannot add orders to a completed or cancelled encounter.")


def ensure_encounter_billable(encounter) -> None:
    if encounter.status == "cancelled":
        raise ValueError("Cancelled encounters cannot be billed.")


def ensure_encounter_closed_for_final_billing(encounter) -> None:
    if encounter.status != "completed":
        raise ValueError("Encounter must be completed before final billing.")

