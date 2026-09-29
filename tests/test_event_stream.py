import json
from pathlib import Path

from api_ws_suite.validators import validate_order_event, validate_sequence


FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_valid_events_and_sequence():
    events = json.loads((FIXTURES / "events.json").read_text(encoding="utf-8"))
    assert all(validate_order_event(event) == [] for event in events)
    assert validate_sequence(events) == []


def test_malformed_event_is_explained():
    errors = validate_order_event({"event_id": "evt-bad", "status": "unknown", "sequence": -1})
    assert "missing field: order_id" in errors
    assert "unsupported status" in errors
    assert "sequence must be non-negative" in errors


def test_duplicate_and_out_of_order_events_are_detected():
    events = [
        {"event_id": "same", "sequence": 2},
        {"event_id": "same", "sequence": 1},
    ]
    errors = validate_sequence(events)
    assert any("duplicate" in error for error in errors)
    assert any("non-increasing" in error for error in errors)

