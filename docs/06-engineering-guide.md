# Engineering Guide

## Repository patterns

### Gold + verifier (Months)

| File | Responsibility |
|------|----------------|
| `ideal_completion.py` | Reference implementation |
| `tests.py` | unittest cases |
| `testableIC.py` | Importable subset when ideal has side effects |
| `working_ideal_completion.py` | Test-stable variant (`Model/` task) |
| `utils.py` | Task-local helpers |

**Why `working_ideal_completion.py` exists:** `Model/tests.py` imports from it instead of `ideal_completion.py` when the ideal has training side effects or non-determinism.

### A/B pairs (Colosseum)

```
Task/TurnN/Completion{A,B}/*.py
```

Typo variants exist: `CompleitonA`, `completionA` — manifest script handles case variants.

### Test entry point

```python
if __name__ == '__main__':
    unittest.main()
```

## Design decisions

| Decision | Rationale | Tradeoff |
|----------|-----------|----------|
| No shared package | Tasks copied independently during eval work | Duplication (BondAnalyzer in multiple months) |
| unittest not pytest | Stdlib only per task | No shared fixtures |
| Per-task deps | Tasks span diverse domains | No one `pip install` for all |
| Flat folder names | Fast iteration | Typos, inconsistent casing |

## Error handling

Generally minimal — eval tasks assume happy path. TradingBot uses `setup_logger()` for operational logging.

## Parallelism

`ThreadPoolExecutor` in race/TSP tasks for benchmarking concurrent runs — not distributed training.

## File naming issues (known)

| Typo | Count | Action |
|------|-------|--------|
| `CompleitonA` | several | Fix when touching task |
| `tersts.py` | few | Rename to `tests.py` |
| `ideal_compleiton.py` | few | Rename to `ideal_completion.py` |

## Tooling added to repo

| Script | Purpose |
|--------|---------|
| `scripts/generate_task_manifest.py` | Build `TASKS.json` |
| `scripts/list_tasks.py` | Filter/list tasks |
| `scripts/run_tests.py` | Batch unittest runner |
| `scripts/validate_repo.py` | Structure checks |

## Performance considerations

- Selenium tests are slow — run selectively
- TensorFlow/PyTorch tasks may need GPU but work on CPU for small fixtures
- Remove `__pycache__/` from version control (see `.gitignore`)

## Testing strategy

| Level | Mechanism |
|-------|-----------|
| Unit | Per-task `tests.py` |
| Integration | Selenium/Playwright in Month6 Batch3 |
| Repo | `scripts/run_tests.py` (best-effort batch) |
| Validation | `scripts/validate_repo.py` |

## Extension patterns

When adding tasks:

1. Self-contained folder
2. `unittest` imports from local module only
3. Regenerate `TASKS.json`
4. Document extra deps in task comment if non-obvious
