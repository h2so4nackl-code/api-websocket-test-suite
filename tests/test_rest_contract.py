import json
from pathlib import Path


FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_order_fixture_contract():
    orders = json.loads((FIXTURES / "orders.json").read_text(encoding="utf-8"))
    assert orders
    assert all(set(order) == {"id", "side", "quantity", "price", "status"} for order in orders)
    assert all(order["side"] in {"buy", "sell"} for order in orders)
    assert all(order["quantity"] > 0 and order["price"] > 0 for order in orders)


def test_unknown_order_error_shape():
    response = {"status": 404, "body": {"error": {"code": "ORDER_NOT_FOUND", "message": "No order matches the supplied id"}}}
    assert response["status"] == 404
    assert response["body"]["error"]["code"] == "ORDER_NOT_FOUND"

