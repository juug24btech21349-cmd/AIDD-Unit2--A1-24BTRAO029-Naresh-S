# What you still need to do (submission checklist)

The code in this folder is the **project**. The assignment also grades **how you used Cursor** and **GitHub**. Do these in order.

## 1. Confirm the tool (already done if you are in Cursor)

You must use Cursor, not GitHub Copilot. You are already in Cursor Agent.

## 2. Run the project locally

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python -m expense_splitter.cli --demo
```

## 3. Take three screenshots (required)

Open this chat (or a new Cursor Agent chat) and capture:

1. The **zero-shot** scaffold prompt + the generated `ExpenseSplitter` code  
2. The **few-shot** prompt that includes the example docstrings/tests  
3. The **chain-of-thought** prompt that says **“think step by step”** + the rounding/settlement answer  

Save them as:

- `docs/screenshots/01-zero-shot.png`
- `docs/screenshots/02-few-shot.png`
- `docs/screenshots/03-chain-of-thought.png`

Then mention the file names in `docs/PROMPT_LOG.md` (already listed there).

Tip: Windows **Win + Shift + S** to snip the Cursor window.

## 4. Create the GitHub repo (Jain University account)

Suggested name: `AIDD-Unit2-A1-<RollNo>-<YourName>`

- Create the repo on GitHub (public, **or** private and add `shivaprasad-munukuntla` as collaborator).
- Do **not** dump everything in one commit. Use several commits, for example:

  1. `Add expense splitter core module`
  2. `Add Google-style docstrings and unit tests`
  3. `Fix leftover-cent split and settlement`
  4. `Add CLI, demo JSON, and docs`

Commands (after `git init` if needed):

```bash
git add expense_splitter/splitter.py expense_splitter/__init__.py
git commit -m "Add expense splitter core module"

git add tests/test_splitter.py
git commit -m "Add unit tests with Arrange/Act/Assert style"

git add tests/test_settlement.py expense_splitter/cli.py
git commit -m "Add settlement edge-case tests and CLI"

git add README.md docs examples requirements.txt .gitignore tests/test_cli.py
git commit -m "Add README, prompt log, and sample trip JSON"
```

Ask the assistant to create these commits **only if you want that done for you**.

## 5. Fill anything personal in the docs

- Put **your name / roll number** in the GitHub repo name and, if you want, at the top of `README.md`.
- If Cursor felt slow, hit a quota, or you edited a prompt, add that sentence to the reflection in `docs/PROMPT_LOG.md`.

## 6. Submit

1. Push the repo.
2. Copy the GitHub URL.
3. Submit that link in the classroom document as the assignment asks.

## Academic integrity reminder

Do not copy another student’s repo. This log should match **your** Cursor chat. Keep this conversation so the screenshots match the prompts in `docs/PROMPT_LOG.md`.
