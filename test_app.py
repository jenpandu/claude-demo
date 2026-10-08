import pytest

import app as app_module
from app import create_app
from splitter import split_evenly


@pytest.fixture
def client():
    # The store is module-level, so reset it between tests rather than letting
    # one test's expenses leak into the next one's balances.
    app_module._expenses.clear()
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_health_reports_the_configured_currency(client):
    body = client.get("/health").get_json()
    assert body["status"] == "ok"
    assert body["currency"]


def test_split_three_ways():
    assert split_evenly(900, ["ana", "ben", "cal"]) == {
        "ana": 300,
        "ben": 300,
        "cal": 300,
    }


def test_payer_is_credited_the_others_shares(client):
    client.post(
        "/expenses",
        json={
            "amount_cents": 900,
            "paid_by": "ana",
            "participants": ["ana", "ben", "cal"],
        },
    )
    body = client.get("/balances").get_json()
    assert body["balances"]["ana"] == 600
    assert body["balances"]["ben"] == -300
