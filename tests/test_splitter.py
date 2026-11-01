"""Unit tests for the expense splitter.

Style (few-shot): every test uses Arrange / Act / Assert comments and one
clear behaviour per test function.
"""

from decimal import Decimal

import pytest

from expense_splitter.splitter import (
    ExpenseSplitter,
    cents_to_decimal,
    parse_amount_to_cents,
    people_from_names,
    split_evenly,
)


def test_parse_amount_to_cents_rounds_half_up():
    # Arrange
    amount = "10.555"

    # Act
    cents = parse_amount_to_cents(amount)

    # Assert
    assert cents == 1056


def test_cents_to_decimal_keeps_two_places():
    # Arrange
    cents = 1056

    # Act
    value = cents_to_decimal(cents)

    # Assert
    assert value == Decimal("10.56")


def test_split_evenly_distributes_remainder_cents():
    # Arrange
    total_cents = 1000  # 10.00
    n = 3

    # Act
    parts = split_evenly(total_cents, n)

    # Assert
    assert parts == [334, 333, 333]
    assert sum(parts) == total_cents


def test_add_person_rejects_duplicates():
    # Arrange
    splitter = ExpenseSplitter()
    splitter.add_person("Asha")

    # Act / Assert
    with pytest.raises(ValueError, match="already added"):
        splitter.add_person("Asha")


def test_equal_split_three_people_ten_rupees():
    # Arrange
    splitter = people_from_names(["Asha", "Ben", "Chen"])
    splitter.add_expense("Dinner", "10.00", "Asha")

    # Act
    balances = splitter.calculate_balances()

    # Assert
    # Asha paid 10.00 and owes 3.34 of it -> +6.66
    # Ben and Chen each owe 3.33
    assert balances["Asha"] == Decimal("6.66")
    assert balances["Ben"] == Decimal("-3.33")
    assert balances["Chen"] == Decimal("-3.33")
    assert sum(balances.values()) == Decimal("0.00")


def test_expense_for_subset_of_people():
    # Arrange
    splitter = people_from_names(["Asha", "Ben", "Chen"])

    # Act
    splitter.add_expense("Cab", "15.00", "Ben", participants=["Asha", "Ben"])
    balances = splitter.calculate_balances()

    # Assert
    assert balances["Asha"] == Decimal("-7.50")
    assert balances["Ben"] == Decimal("7.50")
    assert balances["Chen"] == Decimal("0.00")


def test_custom_shares_must_sum_to_total():
    # Arrange
    splitter = people_from_names(["Asha", "Ben"])

    # Act / Assert
    with pytest.raises(ValueError, match="Custom shares sum"):
        splitter.add_expense(
            "Snacks",
            "10.00",
            "Asha",
            shares={"Asha": "6.00", "Ben": "3.00"},
        )


def test_unknown_payer_is_rejected():
    # Arrange
    splitter = people_from_names(["Asha"])

    # Act / Assert
    with pytest.raises(ValueError, match="Unknown person"):
        splitter.add_expense("Tea", "2.00", "Ben")
