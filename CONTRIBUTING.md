# Contributing

Thank you for improving this evaluation archive.

## Before you start

1. Read [docs/01-executive-summary.md](docs/01-executive-summary.md) — this is **not** an RL training repo.
2. Run `python scripts/validate_repo.py` after changes.
3. Regenerate the manifest: `python scripts/generate_task_manifest.py`

## Adding a Months eval task

```
Months/<MonthN>/<Section>/<TaskName>/
  ideal_completion.py    # Reference solution
  tests.py               # unittest harness
```

Guidelines:

- Use `unittest` (matches existing corpus).
- Keep tasks self-contained — no shared root package imports.
- Name files consistently: `ideal_completion.py`, `tests.py`.
- Document unusual dependencies in a task-local comment or README snippet.

## Adding a Colosseum A/B task

```
Colosseum/<Branch>/<Week>/<TaskName>/Turn1/
  CompletionA/CompletionA.py
  CompletionB/CompletionB.py
```

## Running tests

```bash
# Single task
cd Months/Month6/multi_turn2/BondAnalyzer && python tests.py

# Batch (tooling only — many tasks need extra pip packages)
python scripts/run_tests.py --month Month6 --limit 10
```

## Code style

- Match surrounding task code.
- Prefer clear function names over heavy abstraction.
- Avoid committing `__pycache__/`, `.pyc`, secrets, or API keys.

## Pull request checklist

- [ ] `python scripts/generate_task_manifest.py` run if tasks added/moved
- [ ] `python scripts/validate_repo.py` passes
- [ ] No secrets in diff
- [ ] Docs updated if structure changes

## Reporting issues

Include: task path, Python version, installed packages, and full test output.
