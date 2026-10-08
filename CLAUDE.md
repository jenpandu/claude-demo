# Ledger — expense sharing API

## Commands
- Run tests: `pytest`
- Run the app: `python app.py` (needs `.env`; copy `.env.example`)

## Conventions
- **All money is integer cents.** Never floats, anywhere.
- Business logic lives in `splitter.py`. `app.py` only parses and serialises.
- Tests go in `test_*.py` at the repo root.

## Invariant
Net balances across a complete set of expenses must sum to exactly zero.
