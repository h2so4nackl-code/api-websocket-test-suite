from __future__ import annotations

import asyncio
import json
import time
from typing import Any

import websockets

from .validators import validate_order_event, validate_sequence


async def probe(
    uri: str,
    attempts: int = 2,
    timeout_seconds: float = 2.0,
    expected_messages: int = 1,
) -> dict[str, Any]:
    """Connect, receive events, validate them, and retry transient failures."""
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    if expected_messages < 1:
        raise ValueError("expected_messages must be at least 1")

    async def receive_messages():
        async with websockets.connect(uri) as socket:
            return [await socket.recv() for _ in range(expected_messages)]

    failures: list[str] = []
    for attempt in range(1, attempts + 1):
        started = time.perf_counter()
        try:
            raw_messages = await asyncio.wait_for(
                receive_messages(), timeout=timeout_seconds
            )
            latency_ms = round((time.perf_counter() - started) * 1_000, 2)
            events: list[Any] = []
            for message_index, raw in enumerate(raw_messages):
                try:
                    events.append(json.loads(raw))
                except (TypeError, UnicodeDecodeError, json.JSONDecodeError):
                    return {
                        "passed": False,
                        "attempt": attempt,
                        "message_count": len(raw_messages),
                        "latency_ms": latency_ms,
                        "errors": [f"malformed JSON at message {message_index}"],
                    }

            errors: list[str] = []
            for message_index, event in enumerate(events):
                errors.extend(
                    f"message {message_index}: {error}"
                    for error in validate_order_event(event)
                )
            if all(isinstance(event, dict) for event in events) and len(events) > 1:
                errors.extend(validate_sequence(events))
            return {
                "passed": not errors,
                "attempt": attempt,
                "message_count": len(events),
                "latency_ms": latency_ms,
                "errors": errors,
            }
        except (OSError, asyncio.TimeoutError, websockets.WebSocketException) as exc:
            failures.append(f"attempt {attempt}: {exc.__class__.__name__}")
    return {
        "passed": False,
        "attempt": attempts,
        "message_count": 0,
        "latency_ms": None,
        "errors": failures,
    }
