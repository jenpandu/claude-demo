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


VALID = {"amount_cents": 900, "paid_by": "ana", "participants": ["ana", "ben"]}


@pytest.mark.parametrize("field", ["amount_cents", "paid_by", "participants"])
def test_missing_field_is_400_not_500(client, field):
    body = {k: v for k, v in VALID.items() if k != field}
    resp = client.post("/expenses", json=body)
    assert resp.status_code == 400
    assert any(field in e for e in resp.get_json()["errors"])


@pytest.mark.parametrize(
    "override",
    [
        {"amount_cents": 9.5},
        {"amount_cents": "900"},
        {"amount_cents": True},
        {"amount_cents": 0},
        {"amount_cents": -100},
        {"paid_by": ""},
        {"paid_by": 7},
        {"participants": []},
        {"participants": "ana"},
        {"participants": ["ana", 3]},
        {"participants": ["ana", "ana"]},
    ],
)
def test_invalid_values_are_400(client, override):
    resp = client.post("/expenses", json={**VALID, **override})
    assert resp.status_code == 400


@pytest.mark.parametrize("raw", [None, "not json", "[1, 2]"])
def test_non_object_body_is_400(client, raw):
    resp = client.post("/expenses", data=raw, content_type="application/json")
    assert resp.status_code == 400


def test_rejected_expense_is_not_stored(client):
    client.post("/expenses", json={"paid_by": "ana"})
    assert client.get("/balances").get_json()["balances"] == {}


def test_valid_expense_still_created(client):
    assert client.post("/expenses", json=VALID).status_code == 201


@pytest.mark.parametrize(
    "amount, participants",
    [(100, ["a", "b", "c"]), (1, ["a", "b"]), (10, ["a", "b", "c", "d", "e", "f", "g"]), (7, ["a"])],
)
def test_split_shares_sum_to_amount(amount, participants):
    shares = split_evenly(amount, participants)
    assert sum(shares.values()) == amount
    assert max(shares.values()) - min(shares.values()) <= 1


def test_split_remainder_goes_to_first_participants_in_order():
    assert split_evenly(100, ["a", "b", "c"]) == {"a": 34, "b": 33, "c": 33}
    assert split_evenly(101, ["a", "b", "c"]) == {"a": 34, "b": 34, "c": 33}


def test_balances_sum_to_zero_for_uneven_splits(client):
    for amount, payer, parts in [
        (100, "ana", ["ana", "ben", "cal"]),
        (1, "ben", ["ana", "ben"]),
        (1001, "cal", ["ana", "ben", "cal", "dee"]),
    ]:
        client.post(
            "/expenses",
            json={"amount_cents": amount, "paid_by": payer, "participants": parts},
        )
    balances = client.get("/balances").get_json()["balances"]
    assert sum(balances.values()) == 0
