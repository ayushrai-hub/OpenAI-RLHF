# Repository Overview

## Purpose

Archive of programming evaluation work: reference implementations, unit test harnesses, and A/B model completion artifacts used to assess coding LLM output quality.

## Research objective (inferred)

Support **model evaluation workflows**:

1. Generate code from prompts (external to this repo)
2. Verify against gold solutions (`Months/`)
3. Or compare competing completions (`Colosseum/`)

This is **evaluation infrastructure data**, not training infrastructure code.

## Supported "algorithms"

**RL algorithms:** None.

**Present instead:**

| Category | Examples in repo |
|----------|------------------|
| Classical CS | A*, Dijkstra, Lagrangian relaxation, TSP |
| Evolutionary | Genetic algorithm (HVAC ductwork) |
| Supervised ML | Keras, PyTorch, XGBoost, CRF |
| Simulation | Monte Carlo photon attenuation |
| Financial | Bond yield curves, arbitrage detection |
| LLM APIs | OpenAI ChatCompletion, LangChain Chroma |

## Intended users

| User | Use case |
|------|----------|
| Evaluators / labelers | Run tests, compare A/B completions |
| Reviewers | Audit reference solutions |
| Researchers (external) | Export preference pairs for DPO/RLHF training elsewhere |
| New engineers | Onboard via docs + `TASKS.json` |

## Maturity assessment

| Area | Rating | Notes |
|------|--------|-------|
| Task coverage | High | 7 months + Colosseum branches |
| Consistency | Low | Typos in filenames, duplicate tasks |
| Build system | None | Per-task dependencies |
| CI/CD | None | Use `scripts/run_tests.py` locally |
| Documentation | Improved | `docs/` + README |

## Active development

Archive status. Use `scripts/generate_task_manifest.py` after adding tasks.

## File statistics

```
Colosseum/   ~596 files
Months/      ~886 files
test/        6 files
triton/      0 files
```

Most common filenames: `CompletionA.py` (206), `CompletionB.py` (205), `ideal_completion.py` (186), `tests.py` (125).
