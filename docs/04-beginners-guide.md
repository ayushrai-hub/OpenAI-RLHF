# Beginner's Guide

*Assumes you know Python. No prior RL knowledge required.*

## What is this repo?

A collection of **coding homework problems with answer keys and grading scripts**. The name "RLHF" is misleading — think "code evaluation archive" instead.

## Core concepts

### 1. Reference solution (`ideal_completion.py`)

The "correct" or exemplar implementation for a programming task. When an LLM generates code, you compare its output against this file.

### 2. Test harness (`tests.py`)

Automated grader using Python's built-in `unittest` module. It imports functions from `ideal_completion.py`, runs them with sample inputs, and checks outputs.

### 3. A/B completions (Colosseum)

Two versions of model-generated code (`CompletionA` vs `CompletionB`). A human picks which is better — useful for training preference models **outside** this repo.

## Your first task (5 minutes)

```bash
cd OpenAI-RLHF
python scripts/generate_task_manifest.py
cd Months/Month6/multi_turn2/BondAnalyzer
python tests.py
```

If tests pass, you see `OK`. If not, read the failure message — often a missing pip package.

## Understanding a Months task

Example folder:

```
BondAnalyzer/
  ideal_completion.py   # BondAnalyzer class — yield curves, arbitrage
  tests.py              # Creates BondAnalyzer, checks math
```

Flow:

1. `tests.py` defines `class TestBondAnalyzer(unittest.TestCase)`
2. `setUp()` creates test data (LIBOR rates, bond prices)
3. Each `test_*` method calls `ideal_completion` and asserts results

## Understanding Colosseum

```
Annotations/Turn1/
  CompletionA/CompletionA.py   # matplotlib precision/recall chart
  CompletionB/CompletionB.py   # may be empty or alternate approach
```

No automated test — the point is **comparison**.

## Common libraries you'll see

| Library | Used for |
|---------|----------|
| `numpy` | Arrays, math |
| `pandas` | Tables, CSV |
| `matplotlib` | Plots |
| `sklearn` | Machine learning |
| `unittest` | Testing |
| `selenium` | Browser automation tests |

## Glossary

| Term | Meaning here |
|------|--------------|
| RLHF | **Not in this repo** — Reinforcement Learning from Human Feedback (training method) |
| Eval task | One folder with solution + tests |
| Gold / ideal | Reference solution |
| Preference pair | CompletionA vs CompletionB |

## What to read next

- [Evaluation Guide](08-evaluation-guide.md) — running tests at scale
- [Months subsystem](projects/months.md) — full corpus tour
- [Developer Onboarding](11-developer-onboarding.md)
