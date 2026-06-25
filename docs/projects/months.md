# Months Subsystem

## Purpose

**Automated coding evaluation** via gold reference implementations and unittest harnesses.

## Problem solved

Objectively verify whether model-generated code meets functional requirements without manual review for every task.

## Architecture

```
Months/
├── Month1/   # ~96 files — early tasks
├── Month2/   # ~105 files — GUI, genetic DCT
├── Month3/   # ~74 files — sorting, optimization
├── Month4/   # ~149 files — finance, audio, algorithms
├── Month5/   # ~229 files — LangChain, OpenAI, XGBoost, Django
├── Month6/   # ~214 files — largest multi-turn batch
└── Month7/   # ~19 files — production-style data scripts
```

## Standard task pattern

```
<TaskFolder>/
  ideal_completion.py      # Gold solution
  tests.py                 # unittest verifier
  [optional] utils.py
  [optional] testableIC.py
  [optional] working_ideal_completion.py
```

## Month6 highlights

| Section | Tasks | Notes |
|---------|-------|-------|
| `multi_turn2/` | Flask, BondAnalyzer, genetic, Model, Kernel, SEM | Core ML/finance/web |
| `Review_multi-turn/Batch1/` | Monte-Carlo, RF, matrix, Vector | Scientific |
| `Review_multi-turn/Batch2/` | CRF, decision (PyTorch), Time-series | ML/NLP |
| `Review_multi-turn/Batch3/` | webtoon, portfolio, electron, firmware | HTML/JS + Selenium |
| `Redo_multi_Needs_work/` | OCR, torch/YOLOS | Needs review |
| `Multi-turn-old-Restart/` | pygame, TSP, beamforming | Older iterations |

## Month7 — LSGV2 scripts

Standalone data analysis scripts (not ideal_completion pattern):

| Path | Purpose |
|------|---------|
| `LSGV2/Prod/Coomera/code*.py` | Geocoding daycare addresses |
| `LSGV2/Prod/ARIMA/code.py` | FRED exchange rate data |
| `LSGV2/Prod/Wind/code.py` | NOAA buoy wind analysis |
| `LSGV2/Onboarding/reactNative/code.py` | GitHub API hooks analyzer |

## Execution

```bash
cd Months/Month6/multi_turn2/BondAnalyzer
python tests.py
```

## Inputs / outputs

| | |
|-|-|
| **Input** | Test fixtures in `setUp()` / `setUpClass()` |
| **Output** | unittest pass/fail |
| **Side effects** | Some tests create temp files (PDF, DOCX) |

## Dependencies

Domain-specific — see [Dependency Guide](../10-dependency-guide.md).

## Tradeoffs

| Pro | Con |
|-----|-----|
| Self-contained tasks | Massive duplication |
| stdlib unittest | No shared fixtures |
| Broad domain coverage | Inconsistent naming |

## Discovering tasks

```bash
python scripts/list_tasks.py --track months --has-tests
python scripts/list_tasks.py --month Month6 --domain finance
```

## Important files by domain

| Domain | Path |
|--------|------|
| Finance | `Month6/multi_turn2/BondAnalyzer/` |
| ML/DL | `Month6/multi_turn2/Model/` |
| Web | `Month6/multi_turn2/Flask/` |
| Evolutionary | `Month6/multi_turn2/genetic/` |
| LLM API | `Month5/Reviews4/OpenAI_API/` |
| RAG | `Month5/Reviews4/LangChain/` |
