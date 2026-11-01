"""CLI tests."""

from pathlib import Path

from expense_splitter.cli import main, run_demo


def test_demo_report_contains_people_and_settlement():
    # Arrange / Act
    report = run_demo()

    # Assert
    assert "Asha" in report
    assert "Dinner" in report
    assert "Settlement:" in report


def test_cli_demo_exits_zero(capsys):
    # Arrange / Act
    code = main(["--demo"])
    captured = capsys.readouterr()

    # Assert
    assert code == 0
    assert "Expense Splitter Report" in captured.out


def test_cli_from_json(tmp_path: Path, capsys):
    # Arrange
    data = tmp_path / "trip.json"
    data.write_text(
        """
        {
          "people": ["Asha", "Ben"],
          "expenses": [
            {"description": "Dinner", "amount": "20.00", "paid_by": "Asha"}
          ]
        }
        """,
        encoding="utf-8",
    )

    # Act
    code = main(["--from-json", str(data)])
    captured = capsys.readouterr()

    # Assert
    assert code == 0
    assert "Dinner" in captured.out
    assert "Ben pays Asha 10.00" in captured.out
