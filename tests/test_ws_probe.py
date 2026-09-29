import asyncio
import json
import socket

from websockets.asyncio.server import serve

from api_ws_suite.ws_probe import probe


def event(event_id="evt-1", sequence=1, status="created"):
    return {
        "event_id": event_id,
        "order_id": "order-1",
        "status": status,
        "sequence": sequence,
        "timestamp": "2026-09-29T10:00:00Z",
    }


async def run_server(handler, assertion, **probe_options):
    async with serve(handler, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]
        result = await probe(f"ws://127.0.0.1:{port}", **probe_options)
    assertion(result)


def test_successful_connection_receives_valid_json_and_measures_latency():
    async def handler(websocket):
        await asyncio.sleep(0.02)
        await websocket.send(json.dumps(event()))

    def assertion(result):
        assert result["passed"] is True
        assert result["attempt"] == 1
        assert result["message_count"] == 1
        assert isinstance(result["latency_ms"], float)
        assert result["latency_ms"] >= 10

    asyncio.run(run_server(handler, assertion, attempts=1, timeout_seconds=1.0))


def test_malformed_json_message_is_reported_by_probe():
    async def handler(websocket):
        await websocket.send("not-json")

    def assertion(result):
        assert result["passed"] is False
        assert result["errors"] == ["malformed JSON at message 0"]

    asyncio.run(run_server(handler, assertion, attempts=1))


def test_receive_timeout_is_bounded_and_reported():
    async def handler(websocket):
        await asyncio.sleep(0.2)

    def assertion(result):
        assert result["passed"] is False
        assert result["attempt"] == 1
        assert result["latency_ms"] is None
        assert result["errors"] == ["attempt 1: TimeoutError"]

    asyncio.run(run_server(handler, assertion, attempts=1, timeout_seconds=0.03))


def test_transient_failure_reconnects_within_bounded_attempts():
    connections = 0

    async def handler(websocket):
        nonlocal connections
        connections += 1
        if connections == 1:
            await websocket.close(code=1011, reason="transient test failure")
            return
        await websocket.send(json.dumps(event()))

    def assertion(result):
        assert result["passed"] is True
        assert result["attempt"] == 2
        assert connections == 2

    asyncio.run(run_server(handler, assertion, attempts=2, timeout_seconds=1.0))


def test_connection_failure_stops_after_configured_attempts():
    with socket.socket() as temporary_socket:
        temporary_socket.bind(("127.0.0.1", 0))
        unused_port = temporary_socket.getsockname()[1]

    result = asyncio.run(
        probe(f"ws://127.0.0.1:{unused_port}", attempts=2, timeout_seconds=0.2)
    )

    assert result["passed"] is False
    assert result["attempt"] == 2
    assert len(result["errors"]) == 2
    assert all(error.startswith("attempt ") for error in result["errors"])


def test_invalid_event_contract_is_reported_by_probe():
    async def handler(websocket):
        await websocket.send(json.dumps({"event_id": "evt-bad", "sequence": -1}))

    def assertion(result):
        assert result["passed"] is False
        assert any("missing field: order_id" in error for error in result["errors"])
        assert any("sequence must be non-negative" in error for error in result["errors"])

    asyncio.run(run_server(handler, assertion, attempts=1))


def test_duplicate_event_id_is_detected_on_live_stream():
    async def handler(websocket):
        await websocket.send(json.dumps(event("same", 1)))
        await websocket.send(json.dumps(event("same", 2, "open")))

    def assertion(result):
        assert result["passed"] is False
        assert "duplicate event_id at index 1" in result["errors"]

    asyncio.run(
        run_server(handler, assertion, attempts=1, expected_messages=2)
    )


def test_out_of_order_sequence_is_detected_on_live_stream():
    async def handler(websocket):
        await websocket.send(json.dumps(event("evt-2", 2)))
        await websocket.send(json.dumps(event("evt-1", 1, "open")))

    def assertion(result):
        assert result["passed"] is False
        assert "non-increasing sequence at index 1" in result["errors"]

    asyncio.run(
        run_server(handler, assertion, attempts=1, expected_messages=2)
    )
