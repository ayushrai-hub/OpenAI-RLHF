# Recommendations & Future Work

## Refactoring

| Priority | Action | Rationale |
|----------|--------|-----------|
| High | Rename repo to `coding-eval-corpus` | Reduces RLHF confusion |
| High | Normalize typo filenames | `CompleitonA`, `tersts.py`, `ideal_compleiton.py` |
| Medium | Deduplicate BondAnalyzer copies | Same task in Month4, Month6, Colosseum |
| Medium | Remove `__pycache__` from git | Cleaner archive |
| Low | Populate or delete `triton/` | Empty placeholder |

## Performance

- Run Selenium tests in CI only on changed web tasks
- Cache pip dependencies per domain in CI
- TradingBot: add rate-limit backoff

## Documentation (completed in this pass)

- [x] `docs/` guide set
- [x] Rewritten `README.md`
- [x] `CONTRIBUTING.md`
- [x] `TASKS.json` manifest generator

## Testing gaps

| Gap | Recommendation |
|-----|----------------|
| No CI | GitHub Actions: `validate_repo.py` + Month7 smoke tests |
| No TradingBot tests | Mock ccxt exchange |
| No coverage | Optional `pytest-cov` on selected months |
| Selenium fragility | Document chromedriver setup |

## Research directions

If repurposing for RLHF **externally**:

1. **Export Colosseum pairs** → JSONL `{prompt, chosen, rejected}`
2. **Rule-based rewards** → wrap `unittest` as reward function (RLAIF)
3. **Behavior cloning** → train on `ideal_completion.py` corpus
4. **Contamination checks** → train/test split by task id

## Scripts to add (future)

| Script | Purpose |
|--------|---------|
| `export_preferences.py` | Colosseum → JSONL |
| `export_demonstrations.py` | Months ideals → JSONL |
| `check_deps.py` | Parse imports, suggest requirements |

## Suggested CI workflow

```yaml
# .github/workflows/validate.yml (future)
- run: python scripts/validate_repo.py
- run: python scripts/generate_task_manifest.py
- run: python scripts/run_tests.py --month Month7 --limit 5
```
