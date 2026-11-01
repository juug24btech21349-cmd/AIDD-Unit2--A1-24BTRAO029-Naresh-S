"""Command-line interface for the expense splitter."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from expense_splitter.splitter import ExpenseSplitter


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(description="Split group expenses and settle balances.")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a sample trip (Asha, Ben, Chen) and print the report.",
    )
    parser.add_argument(
        "--from-json",
        metavar="PATH",
        help="Load people and expenses from a JSON file and print the report.",
    )
    return parser


def run_demo() -> str:
    """Build a sample trip used in the README and prompt log."""
    splitter = ExpenseSplitter()
    splitter.add_person("Asha")
    splitter.add_person("Ben")
    splitter.add_person("Chen")
    splitter.add_expense("Dinner", "10.00", "Asha")
    splitter.add_expense("Cab", "15.00", "Ben", participants=["Asha", "Ben"])
    splitter.add_expense(
        "Museum",
        "9.00",
        "Chen",
        shares={"Asha": "2.00", "Ben": "3.00", "Chen": "4.00"},
    )
    return splitter.format_report()


def load_from_json(path: Path) -> str:
    """Load a group from JSON and return the report.

    Expected shape::

        {
          "people": ["Asha", "Ben"],
          "expenses": [
            {"description": "Dinner", "amount": "20.00", "paid_by": "Asha"}
          ]
        }
    """
    payload: Dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    splitter = ExpenseSplitter()
    for name in payload.get("people", []):
        splitter.add_person(str(name))
    for item in payload.get("expenses", []):
        splitter.add_expense(
            description=item["description"],
            amount=item["amount"],
            paid_by=item["paid_by"],
            participants=item.get("participants"),
            shares=item.get("shares"),
        )
    return splitter.format_report()


def main(argv: list[str] | None = None) -> int:
    """Entry point used by ``python -m expense_splitter.cli``."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.from_json:
        print(load_from_json(Path(args.from_json)))
        return 0
    if args.demo:
        print(run_demo())
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
