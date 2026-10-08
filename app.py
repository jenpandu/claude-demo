"""A small expense-sharing API. Flask, in-memory, no database.

Kept deliberately thin: the HTTP layer parses and serialises, and every
decision about money lives in splitter.py. That separation is what lets the
interesting logic be unit tested without spinning up a web server.
"""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from splitter import balances

load_dotenv()

# Fail fast rather than defaulting. A config value that silently falls back to
# something plausible produces a bug you find in production; one that refuses
# to start produces a bug you find in a second.
CURRENCY = os.environ["LEDGER_CURRENCY"]

# Module-level store. Fine for a teaching app, wrong for anything real -- it is
# per-process, so it is lost on restart and not shared between workers.
_expenses = []


def create_app():
    """Application factory, as built in Week 2."""
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return jsonify(status="ok", currency=CURRENCY)

    @app.post("/expenses")
    def add_expense():
        body = request.get_json(silent=True) or {}
        _expenses.append(
            {
                "amount_cents": body["amount_cents"],
                "paid_by": body["paid_by"],
                "participants": body["participants"],
            }
        )
        return jsonify(ok=True), 201

    @app.get("/balances")
    def get_balances():
        people = sorted(
            {p for e in _expenses for p in e["participants"]}
            | {e["paid_by"] for e in _expenses}
        )
        return jsonify(currency=CURRENCY, balances=balances(_expenses, people))

    return app


if __name__ == "__main__":
    create_app().run(port=int(os.environ.get("PORT", "5000")))
