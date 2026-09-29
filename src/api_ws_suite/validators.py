from __future__ import annotations

from datetime import datetime
from typing import Any


def validate_order_event(event: Any) -> list[str]:
    """Return human-readable contract failures for a fictional order event."""
    if not isinstance(event, dict):
        return ["event must be an object"]
    errors: list[str] = []
    required = {"event_id": str, "order_id": str, "status": str, "sequence": int, "timestamp": str}
    for field, expected_type in required.items():
        if field not in event:
            errors.append(f"missing field: {field}")
        elif not isinstance(event[field], expected_type):
            errors.append(f"invalid type for {field}")
    if event.get("status") not in {"created", "open", "filled", "cancelled", "rejected"}:
        errors.append("unsupported status")
    if isinstance(event.get("sequence"), int) and event["sequence"] < 0:
        errors.append("sequence must be non-negative")
    if isinstance(event.get("timestamp"), str):
        try:
            datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            errors.append("timestamp must be ISO 8601")
    return errors


def validate_sequence(events: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    previous = -1
    for index, event in enumerate(events):
        event_id = event.get("event_id")
        sequence = event.get("sequence")
        if event_id in seen:
            errors.append(f"duplicate event_id at index {index}")
        if isinstance(event_id, str):
            seen.add(event_id)
        if not isinstance(sequence, int) or sequence <= previous:
            errors.append(f"non-increasing sequence at index {index}")
        if isinstance(sequence, int):
            previous = sequence
    return errors

