"""Settlement and rounding edge-case tests (chain-of-thought coverage)."""

from decimal import Decimal

from expense_splitter.splitter import ExpenseSplitter, people_from_names


def test_settlement_two_debtors_one_creditor():
    # Arrange
    splitter = people_from_names(["Asha", "Ben", "Chen"])
    splitter.add_expense("Hotel", "30.00", "Asha")

    # Act
    transfers = splitter.settle_debts()

    # Assert
    assert ("Ben", "Asha", Decimal("10.00")) in transfers
    assert ("Chen", "Asha", Decimal("10.00")) in transfers
    assert len(transfers) == 2


def test_settlement_zeroes_all_balances():
    # Arrange
    splitter = people_from_names(["Asha", "Ben", "Chen"])
    splitter.add_expense("Dinner", "10.00", "Asha")
    splitter.add_expense("Cab", "15.00", "Ben", participants=["Asha", "Ben"])
    splitter.add_expense(
        "Museum",
        "9.00",
        "Chen",
        shares={"Asha": "2.00", "Ben": "3.00", "Chen": "4.00"},
    )

    # Act
    transfers = splitter.settle_debts()
    simulated = {name: 0 for name in splitter.people}
    for debtor, creditor, amount in transfers:
        cents = int(amount * 100)
        # Debtor's negative balance moves toward zero; creditor's positive
        # balance is reduced by the same payment.
        simulated[debtor] += cents
        simulated[creditor] -= cents
    original = {name: int(value * 100) for name, value in splitter.calculate_balances().items()}

    # Assert — applying the suggested payments should cancel every net balance
    combined = {name: original[name] + simulated[name] for name in original}
    assert all(value == 0 for value in combined.values())


def test_empty_group_has_no_settlement():
    # Arrange
    splitter = ExpenseSplitter()

    # Act
    transfers = splitter.settle_debts()

    # Assert
    assert transfers == []


def test_report_mentions_all_settled_when_balanced():
    # Arrange
    splitter = people_from_names(["Asha", "Ben"])
    splitter.add_expense("Lunch", "20.00", "Asha", shares={"Asha": "10.00", "Ben": "10.00"})
    splitter.add_expense("Tickets", "20.00", "Ben", shares={"Asha": "10.00", "Ben": "10.00"})

    # Act
    report = splitter.format_report()

    # Assert
    assert "All settled." in report
