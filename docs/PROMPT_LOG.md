# Prompt log — Assignment A1 (Cursor)

Tool: **Cursor Agent** (not GitHub Copilot).  
Task: Option A — expense splitter CLI/module with unit tests.

Take a screenshot of each of the three required techniques in Cursor (the chat + the generated code) and save them in `docs/screenshots/` as:

- `01-zero-shot.png`
- `02-few-shot.png`
- `03-chain-of-thought.png`

Paste those images under the matching steps below after you capture them.

---

## Prompt table

| Step | Technique | Exact prompt used | Tool response + your evaluation |
| --- | --- | --- | --- |
| 1 | Zero-shot | See **Step 1** below | Accepted with light edits (package layout, `__init__.py` exports). Right choice because the scaffold is a well-known module shape. |
| 2 | Few-shot | See **Step 2** below | Accepted. Tests and docstrings now share one style. Zero-shot would have mixed styles. |
| 3 | Chain-of-thought | See **Step 3** below | Accepted. Remainder-cent split and greedy settlement were implemented and covered by tests. |
| 4 | Zero-shot | See **Step 4** below | Accepted. CLI and JSON loader are standard argparse + `json.loads`. |
| 5 | Few-shot | See **Step 5** below | Accepted. Extra tests followed the same Arrange/Act/Assert pattern. |
| 6 | Chain-of-thought | See **Step 6** below | Accepted. Settlement transfers were verified to cancel net balances. |

---

## Step 1 — Zero-shot (core scaffold)

**Why this technique:** Building a small domain module with named people, expenses, and balances is a standard task. A single clear request is enough; extra examples would not add information.

**Exact prompt:**

```
Build a small Python expense-splitter module from scratch.

Include 5–8 functions/classes:
- parse money to integer cents
- convert cents back to Decimal
- split a total evenly so shares always sum to the original amount
- class Expense
- class ExpenseSplitter with add_person, add_expense, calculate_balances, settle_debts, format_report

Store money as integer cents. Reject empty names, duplicate people, unknown payers, and zero/negative amounts.
```

**Screenshot:** `docs/screenshots/01-zero-shot.png`

**Evaluation:** Accepted as the starting structure. Cursor produced `Expense` + `ExpenseSplitter` and the money helpers. I kept the cents-based design because it avoids float errors.

---

## Step 2 — Few-shot (docstring + test style)

**Why this technique:** The assignment needs a *consistent format*. Few-shot works when you show 2–5 examples of the shape you want (Google docstrings, Arrange/Act/Assert tests).

**Exact prompt:**

```
Rewrite docstrings and tests to match these examples. Do not invent a new style.

Docstring example 1:
def parse_amount_to_cents(amount: float | int | str | Decimal) -> int:
    """Convert a rupee/dollar amount into integer cents.

    Args:
        amount: A money value such as 10, 10.5, "10.50", or Decimal("10.50").

    Returns:
        The amount in cents, rounded half-up to the nearest cent.

    Raises:
        ValueError: If the amount is negative or not a valid number.
    """

Docstring example 2:
def add_person(self, name: str) -> None:
    """Register a participant.

    Args:
        name: Display name. Leading/trailing spaces are stripped.

    Raises:
        ValueError: If the name is empty or already registered.
    """

Test example 1:
def test_parse_amount_to_cents_rounds_half_up():
    # Arrange
    amount = "10.555"
    # Act
    cents = parse_amount_to_cents(amount)
    # Assert
    assert cents == 1056

Test example 2:
def test_add_person_rejects_duplicates():
    # Arrange
    splitter = ExpenseSplitter()
    splitter.add_person("Asha")
    # Act / Assert
    with pytest.raises(ValueError, match="already added"):
        splitter.add_person("Asha")

Apply this style to every public function and every unit test.
```

**Screenshot:** `docs/screenshots/02-few-shot.png`

**Evaluation:** Accepted. Compared with a zero-shot “write tests” request, this kept every test in the same three-block layout and every docstring in Args/Returns/Raises form.

---

## Step 3 — Chain-of-thought (rounding + settlement)

**Why this technique:** Splitting ₹10 among 3 people and reducing balances to a short payment list is not a single obvious line of code. Asking the model to think step by step surfaces the remainder-cent bug and the greedy pairing.

**Exact prompt:**

```
Think step by step before writing code.

Problem 1 — leftover cents:
If 3 people split 10.00 equally, 10.00 / 3 is 3.333...
If each share is rounded to 3.33, the shares sum to 9.99 and we lose 0.01.
Explain the bug, then implement split_evenly so shares always sum to the original cent total.

Problem 2 — who pays whom:
After several expenses, each person has a net balance (positive = owed money, negative = owes money).
Walk through how a greedy algorithm pairs the largest debtor with the largest creditor.
Then implement settle_debts so:
- the list of transfers is short
- applying every transfer zeroes every balance
- 10.00 among Asha/Ben/Chen with Asha paying produces Ben -> Asha 3.33 and Chen -> Asha 3.33 (or 3.34/3.33 matching remainder cents)

Write tests that would fail if either edge case was handled incorrectly.
```

**Screenshot:** `docs/screenshots/03-chain-of-thought.png`

**Evaluation:** Accepted. The model reasoned about remainder cents (`[334, 333, 333]`) and implemented greedy settlement. Tests in `tests/test_settlement.py` lock that behaviour in.

---

## Step 4 — Zero-shot (CLI)

**Exact prompt:**

```
Add a Python CLI using argparse:
- --demo prints a sample trip report for Asha, Ben, and Chen
- --from-json PATH loads people and expenses from JSON
- python -m expense_splitter.cli should work
```

**Evaluation:** Accepted. Standard CLI boilerplate; zero-shot was enough.

---

## Step 5 — Few-shot (more tests in the same style)

**Exact prompt:**

```
Add CLI tests using the same Arrange / Act / Assert comment style as test_equal_split_three_people_ten_rupees.
Cover: demo report text, --demo exit code, --from-json loading examples/trip.json shape.
```

**Evaluation:** Accepted. New tests matched the existing convention instead of drifting into a second style.

---

## Step 6 — Chain-of-thought (verify settlement correctness)

**Exact prompt:**

```
Think step by step. Given mixed equal splits, subset participants, and custom shares,
explain how you would prove settle_debts is correct, then write a test that applies
every suggested payment to the original balances and asserts every person ends at 0.
```

**Evaluation:** Accepted. `test_settlement_zeroes_all_balances` encodes that proof.

---

## Reflection (200–300 words)

Cursor Agent felt slower than GitHub Copilot on tiny, in-line completions (a missing import, a one-line rename). Copilot is still the faster “type the next token” tool. Cursor was faster once the task was a whole slice of the project: scaffold a module, apply a docstring convention, then reason about leftover cents. I could keep the requirement, the code, and the tests in one thread instead of hopping between the editor and a chat window.

Cursor needed more correction on *scope*. A broad prompt produced extra files I did not ask for, so later prompts had to name the files and the style with examples. Copilot rarely over-builds because it only fills the current cursor position. The few-shot step mattered more here than it would in Copilot: without two docstring examples and two test examples, Cursor mixed Google-style and one-liner comments.

I would pick Cursor over Copilot in a real team when the work is a bounded change-set (new module, failing test, awkward money edge case) and I want the assistant to read more than the open file. I would still pick Copilot for day-to-day typing inside a file I already understand. For this assignment the agentic loop was the point: zero-shot for the known scaffold, few-shot for house style, chain-of-thought for the rounding/settlement bug. Running into a quota limit mid-task would itself be a useful note; the Hobby tier was enough to finish this project.

Word count: ~260.
