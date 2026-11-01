# AIDD Unit 2 — Assignment A1: Expense Splitter

repo link:https://github.com/juug24btech21349-cmd/AIDD-Unit2--A1-24BTRAO029-Naresh-S.git


Small Python CLI that records group expenses, splits them evenly or by custom shares, and prints a **minimal settlement** (who should pay whom).

**AI tool used:** Cursor (Agent mode) — not GitHub Copilot.

## Prompting techniques (one-line each)

| Technique | Where it was used |
| --- | --- |
| **Zero-shot** | Scaffolding the core module (`Expense`, `ExpenseSplitter`, add person/expense, balances). |
| **Few-shot** | Enforcing Google-style docstrings and Arrange/Act/Assert unit-test layout. |
| **Chain-of-thought** | Rounding leftover cents on equal splits, and the greedy “who pays whom” settlement. |

Full prompt log, screenshots, and reflection: [`docs/PROMPT_LOG.md`](docs/PROMPT_LOG.md).

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the demo

```bash
python -m expense_splitter.cli --demo
```

Load your own trip:

```bash
python -m expense_splitter.cli --from-json examples/trip.json
```

## Tests

```bash
python -m pytest -q
```

## Project layout

```
expense_splitter/   # library + CLI
tests/              # unit tests
docs/               # prompt log and screenshots
examples/           # sample JSON trip
```
