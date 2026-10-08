# Ledger

A small expense-sharing API. A group pays for things; this works out who owes
whom.

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate      # Windows Git Bash
# source .venv/bin/activate        # macOS / Linux
pip install -e ".[dev]"
cp .env.example .env
```

Dependencies live in `pyproject.toml`. The `[dev]` extra adds pytest; without
it you get just what the app needs to run.

## Run

```bash
python app.py          # http://localhost:5000
pytest                 # test suite
```

## Endpoints

| Method | Path | Does |
|---|---|---|
| `GET` | `/health` | Liveness, and the configured currency |
| `POST` | `/expenses` | Record an expense |
| `GET` | `/balances` | Net position per person |

### Recording an expense

```bash
curl -X POST localhost:5000/expenses \
  -H 'Content-Type: application/json' \
  -d '{"amount_cents": 1000, "paid_by": "ana", "participants": ["ana","ben","cal"]}'
```

`amount_cents` is an integer. All money in this project is integer cents.

### Reading balances

```bash
curl localhost:5000/balances
```

A positive balance means that person is owed money; negative means they owe it.

## Known gaps

This is a teaching codebase, not a finished product:

- Expenses are held in memory, so they're lost on restart.
- `POST /expenses` doesn't validate its input.
- There's no way to settle up — you can see who owes what, but not the
  transactions that would clear it.
