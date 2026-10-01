# API & WebSocket Test Suite

A personal QA portfolio project demonstrating REST contract checks and WebSocket event-stream validation with synthetic local fixtures. It covers connectivity logic, retry behavior, malformed messages, event ordering, duplicate detection, latency evidence, and automated test reports.

No live trading account, private endpoint, wallet, production credential, or proprietary event is used.

## Coverage

- REST success and error contracts
- Required fields, types, enums, and numeric boundaries
- WebSocket connection, receive timeout, and bounded retry logic
- Malformed JSON and invalid event-state handling
- Duplicate event IDs and out-of-order sequence detection
- ISO 8601 timestamp validation
- Latency captured by the reusable WebSocket probe
- Console, JSON, and JUnit-compatible automated reports

## Run locally

Create and activate the virtual environment before installing dependencies. On Windows PowerShell, use `.\.venv\Scripts\Activate.ps1` instead of `source .venv/bin/activate`.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest -q
pytest --junitxml=reports/junit.xml
```

The tests are deterministic. Contract tests use files in `fixtures/`, while probe integration tests start an ephemeral WebSocket server on `127.0.0.1`. They do not contact an external service.

## Evidence

- [`fixtures/orders.json`](fixtures/orders.json) contains fictional REST resources.
- [`fixtures/events.json`](fixtures/events.json) contains a valid fictional event lifecycle.
- [`tests/test_rest_contract.py`](tests/test_rest_contract.py) checks positive and negative REST contracts.
- [`tests/test_event_stream.py`](tests/test_event_stream.py) verifies message shape and stream order.
- [`tests/test_ws_probe.py`](tests/test_ws_probe.py) exercises real loopback WebSocket connections, messages, malformed JSON, timeout, bounded reconnect, latency, invalid contracts, duplicate IDs, and ordering.
- [`reports/sample-summary.json`](reports/sample-summary.json) shows a sanitized result summary.

## Reusable probe

`api_ws_suite.ws_probe.probe()` connects to a supplied WebSocket URI, waits for one or more messages, measures elapsed time, validates JSON, event contracts, duplicate IDs, and sequence order, and retries bounded transient failures. It is intentionally not pointed at a public service by default.

## Project structure

```text
src/api_ws_suite/   validators and WebSocket probe
fixtures/           synthetic orders and events
tests/              REST and event-stream coverage
reports/            sanitized sample result
```

## Limitations

- This is an educational portfolio suite, not a load-testing tool.
- Reconnect behavior is verified against a deterministic loopback server; production-grade backoff and jitter are out of scope.
- The order/event domain is fictional and does not reproduce a private platform protocol.

## Suggested GitHub description

Local REST and WebSocket QA suite with contract, reconnect, malformed-message, ordering, latency, and JUnit reporting examples.

## Suggested topics

`api-testing`, `websocket`, `software-testing`, `quality-assurance`, `python`, `pytest`, `test-automation`, `json`

## License

MIT
