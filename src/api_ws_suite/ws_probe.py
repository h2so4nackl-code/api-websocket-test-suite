from __future__ import annotations

import asyncio
import json
import time
from typing import Any

import websockets

from .validators import validate_order_event


async def probe(uri: str, attempts: int = 2, timeout_seconds: float = 2.0) -> dict[str, Any]:
    """Connect, validate one event, and retry transient connection failures."""
    failures: list[str] = []
    for attempt in range(1, attempts + 1):
        started = time.perf_counter()
        try:
            async with asyncio.timeout(timeout_seconds):
                async with websockets.connect(uri) as socket:
                    raw = await socket.recv()
            latency_ms = round((time.perf_counter() - started) * 1_000, 2)
            try:
                event = json.loads(raw)
            except json.JSONDecodeError:
                return {"passed": False, "attempt": attempt, "latency_ms": latency_ms, "errors": ["malformed JSON"]}
            errors = validate_order_event(event)
            return {"passed": not errors, "attempt": attempt, "latency_ms": latency_ms, "errors": errors}
        except (OSError, TimeoutError, websockets.WebSocketException) as exc:
            failures.append(f"attempt {attempt}: {exc.__class__.__name__}")
    return {"passed": False, "attempt": attempts, "latency_ms": None, "errors": failures}

