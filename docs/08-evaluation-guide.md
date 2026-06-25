# Evaluation Guide

## Evaluation modes

| Mode | Track | Verdict source |
|------|-------|----------------|
| Automated | Months | `unittest` assertions |
| Human | Colosseum | Labeler prefers A or B |

## Running a single task

```bash
cd Months/Month6/multi_turn2/BondAnalyzer
python tests.py -v
```

## Batch execution

```bash
# Generate index first
python scripts/generate_task_manifest.py

# Run up to 10 Month6 tasks (install deps as failures occur)
python scripts/run_tests.py --month Month6 --limit 10

# Single task via tooling
python scripts/run_tests.py --path Months/Month6/multi_turn2/Flask

# Fail on first error
python scripts/run_tests.py --month Month7 --fail-fast
```

## Discovering tasks

```bash
# All Months tasks with tests
python scripts/list_tasks.py --track months --has-tests

# Finance domain
python scripts/list_tasks.py --domain finance

# JSON output
python scripts/list_tasks.py --track months --json
```

## Metrics

| Metric | Definition |
|--------|------------|
| **Pass rate** | `passed / (passed + failed)` from `run_tests.py` |
| **Coverage** | Not measured repo-wide |
| **Preference accuracy** | N/A — Colosseum requires human labels |

## Test types

### unittest (majority)

Standard `TestCase` with `setUp`, `test_*` methods.

### Selenium (Month6 Batch3)

Browser-driven HTML/JS tests. Requires:

```bash
pip install selenium
# + browser driver (chromedriver)
```

### Playwright (`playright/` task)

Similar to Selenium — browser automation.

### File-generating tests

`Flask/tests.py` creates `test.pdf`, `test.docx`, `test.odt` in cwd — cleaned by `.gitignore`.

## Interpreting failures

| Symptom | Likely cause |
|---------|--------------|
| `ModuleNotFoundError` | Install missing package |
| `ImportError: ideal_completion` | Wrong working directory |
| Selenium timeout | Missing driver / headless setup |
| TensorFlow OOM | Use CPU or smaller fixture |

## Benchmarks

No standardized benchmark suite. `Months/Month7/LSGV2/Prod/code/sort.py` benchmarks sorting algorithms — standalone script, not integrated.

## Colosseum evaluation workflow

1. Open `TurnN/CompletionA` and `CompletionB`
2. Compare against prompt/requirements (external)
3. Record preference (external tooling)

No in-repo scoring for Colosseum.

## Validation

```bash
python scripts/validate_repo.py
```

Checks required directories, manifest presence, empty `triton/`, `__pycache__` warnings.
