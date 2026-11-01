"""Core expense-splitting logic.

Money is stored as integer cents so equal splits and settlements never
lose or invent a penny because of floating-point rounding.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


def parse_amount_to_cents(amount: float | int | str | Decimal) -> int:
    """Convert a rupee/dollar amount into integer cents.

    Args:
        amount: A money value such as 10, 10.5, "10.50", or Decimal("10.50").

    Returns:
        The amount in cents, rounded half-up to the nearest cent.

    Raises:
        ValueError: If the amount is negative or not a valid number.
    """
    try:
        quantized = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except Exception as exc:  # noqa: BLE001 — surface a clear student-facing error
        raise ValueError(f"Invalid amount: {amount!r}") from exc
    if quantized < 0:
        raise ValueError("Amount cannot be negative")
    return int(quantized * 100)


def cents_to_decimal(cents: int) -> Decimal:
    """Convert integer cents back to a two-decimal money value.

    Args:
        cents: Amount in cents.

    Returns:
        A Decimal quantized to two fractional digits.
    """
    return (Decimal(cents) / Decimal(100)).quantize(Decimal("0.01"))


def split_evenly(total_cents: int, n: int) -> List[int]:
    """Split total_cents across n people so the parts sum exactly to the total.

    Remainder cents are given to the first people in order. Example: 1000 cents
    among 3 people becomes [334, 333, 333].

    Args:
        total_cents: Whole-cent total to divide.
        n: Number of participants. Must be at least 1.

    Returns:
        A list of n integer cent shares that sum to total_cents.

    Raises:
        ValueError: If n is less than 1.
    """
    if n < 1:
        raise ValueError("Need at least one participant to split an expense")
    base, remainder = divmod(total_cents, n)
    return [base + (1 if i < remainder else 0) for i in range(n)]


@dataclass(frozen=True)
class Expense:
    """One paid cost shared by a subset of the group.

    Attributes:
        description: Short label such as "Dinner" or "Cab".
        amount_cents: Total paid, in cents.
        paid_by: Name of the person who paid.
        shares_cents: Mapping of participant name -> cents they owe for this item.
    """

    description: str
    amount_cents: int
    paid_by: str
    shares_cents: Dict[str, int]


class ExpenseSplitter:
    """Track people, expenses, running balances, and a minimal settlement."""

    def __init__(self) -> None:
        self._people: List[str] = []
        self._expenses: List[Expense] = []

    @property
    def people(self) -> Tuple[str, ...]:
        """Return participant names in the order they were added."""
        return tuple(self._people)

    @property
    def expenses(self) -> Tuple[Expense, ...]:
        """Return recorded expenses in chronological order."""
        return tuple(self._expenses)

    def add_person(self, name: str) -> None:
        """Register a participant.

        Args:
            name: Display name. Leading/trailing spaces are stripped.

        Raises:
            ValueError: If the name is empty or already registered.
        """
        cleaned = name.strip()
        if not cleaned:
            raise ValueError("Person name cannot be empty")
        if cleaned in self._people:
            raise ValueError(f"Person already added: {cleaned}")
        self._people.append(cleaned)

    def add_expense(
        self,
        description: str,
        amount: float | int | str | Decimal,
        paid_by: str,
        participants: Optional[Sequence[str]] = None,
        shares: Optional[Dict[str, float | int | str | Decimal]] = None,
    ) -> Expense:
        """Record an expense and how it should be split.

        Equal split is the default. Pass ``shares`` for an unequal split; those
        share values must sum to ``amount`` (within one cent after rounding).

        Args:
            description: What the money was spent on.
            amount: Total paid by ``paid_by``.
            paid_by: Person who paid. Must already be in the group.
            participants: Who shares the cost. Defaults to everyone.
            shares: Optional mapping of name -> amount for an unequal split.

        Returns:
            The stored Expense.

        Raises:
            ValueError: If people are unknown, the description is empty, the
                amount is invalid, or custom shares do not add up.
        """
        label = description.strip()
        if not label:
            raise ValueError("Expense description cannot be empty")
        payer = paid_by.strip()
        self._require_person(payer)

        total_cents = parse_amount_to_cents(amount)
        if total_cents == 0:
            raise ValueError("Expense amount must be greater than zero")

        if shares is not None:
            share_cents = self._shares_from_custom(shares, total_cents)
        else:
            names = self._resolve_participants(participants)
            parts = split_evenly(total_cents, len(names))
            share_cents = dict(zip(names, parts))

        expense = Expense(
            description=label,
            amount_cents=total_cents,
            paid_by=payer,
            shares_cents=share_cents,
        )
        self._expenses.append(expense)
        return expense

    def calculate_balances(self) -> Dict[str, Decimal]:
        """Return net balance per person.

        A positive balance means the group owes that person money. A negative
        balance means that person still owes the group.

        Returns:
            Mapping of name -> signed Decimal amount.
        """
        cents = self._balance_cents()
        return {name: cents_to_decimal(value) for name, value in cents.items()}

    def settle_debts(self) -> List[Tuple[str, str, Decimal]]:
        """Produce a small list of payments that zero every balance.

        Uses a greedy pairing of the largest debtor with the largest creditor.
        Think of it as: keep paying the person who is owed the most until
        nobody is in the red.

        Returns:
            A list of (debtor, creditor, amount) tuples.
        """
        balances = self._balance_cents()
        debtors: List[List[object]] = [
            [name, -cents] for name, cents in balances.items() if cents < 0
        ]
        creditors: List[List[object]] = [
            [name, cents] for name, cents in balances.items() if cents > 0
        ]
        debtors.sort(key=lambda row: row[1], reverse=True)
        creditors.sort(key=lambda row: row[1], reverse=True)

        transfers: List[Tuple[str, str, Decimal]] = []
        i = 0
        j = 0
        while i < len(debtors) and j < len(creditors):
            debtor_name, debt = debtors[i][0], int(debtors[i][1])
            creditor_name, credit = creditors[j][0], int(creditors[j][1])
            payment = min(debt, credit)
            if payment > 0:
                transfers.append((str(debtor_name), str(creditor_name), cents_to_decimal(payment)))
            debtors[i][1] = debt - payment
            creditors[j][1] = credit - payment
            if int(debtors[i][1]) == 0:
                i += 1
            if int(creditors[j][1]) == 0:
                j += 1
        return transfers

    def format_report(self) -> str:
        """Build a printable summary of people, expenses, balances, and settlement.

        Returns:
            A multi-line report string.
        """
        lines = ["Expense Splitter Report", "=======================", ""]
        lines.append("People: " + (", ".join(self._people) if self._people else "(none)"))
        lines.append("")
        lines.append("Expenses:")
        if not self._expenses:
            lines.append("  (none)")
        else:
            for expense in self._expenses:
                amount = cents_to_decimal(expense.amount_cents)
                lines.append(
                    f"  - {expense.description}: {amount} paid by {expense.paid_by}"
                )
                share_bits = ", ".join(
                    f"{name}={cents_to_decimal(cents)}"
                    for name, cents in expense.shares_cents.items()
                )
                lines.append(f"    shares: {share_bits}")
        lines.append("")
        lines.append("Balances (positive = others owe them):")
        balances = self.calculate_balances()
        if not balances:
            lines.append("  (none)")
        else:
            for name, value in balances.items():
                lines.append(f"  {name}: {value}")
        lines.append("")
        lines.append("Settlement:")
        settlements = self.settle_debts()
        if not settlements:
            lines.append("  All settled.")
        else:
            for debtor, creditor, amount in settlements:
                lines.append(f"  {debtor} pays {creditor} {amount}")
        return "\n".join(lines)

    def _require_person(self, name: str) -> None:
        if name not in self._people:
            raise ValueError(f"Unknown person: {name}")

    def _resolve_participants(self, participants: Optional[Sequence[str]]) -> List[str]:
        if not self._people:
            raise ValueError("Add at least one person before recording an expense")
        if participants is None:
            return list(self._people)
        names = [item.strip() for item in participants]
        if not names:
            raise ValueError("Expense must have at least one participant")
        seen = set()
        ordered: List[str] = []
        for name in names:
            self._require_person(name)
            if name in seen:
                raise ValueError(f"Duplicate participant: {name}")
            seen.add(name)
            ordered.append(name)
        return ordered

    def _shares_from_custom(
        self,
        shares: Dict[str, float | int | str | Decimal],
        total_cents: int,
    ) -> Dict[str, int]:
        if not shares:
            raise ValueError("Custom shares cannot be empty")
        share_cents: Dict[str, int] = {}
        running = 0
        for raw_name, raw_amount in shares.items():
            name = str(raw_name).strip()
            self._require_person(name)
            cents = parse_amount_to_cents(raw_amount)
            share_cents[name] = cents
            running += cents
        if running != total_cents:
            raise ValueError(
                f"Custom shares sum to {cents_to_decimal(running)}, "
                f"but the expense is {cents_to_decimal(total_cents)}"
            )
        return share_cents

    def _balance_cents(self) -> Dict[str, int]:
        balances = {name: 0 for name in self._people}
        for expense in self._expenses:
            balances[expense.paid_by] += expense.amount_cents
            for name, cents in expense.shares_cents.items():
                balances[name] -= cents
        return balances


def people_from_names(names: Iterable[str]) -> ExpenseSplitter:
    """Create a splitter preloaded with the given people.

    Args:
        names: Participant names to register.

    Returns:
        A new ExpenseSplitter containing those people.
    """
    splitter = ExpenseSplitter()
    for name in names:
        splitter.add_person(name)
    return splitter
