# Colosseum Subsystem

## Purpose

Store **A/B model completion pairs** across multi-turn conversational coding tasks for human preference labeling.

## Problem solved

When an LLM iterates on code over multiple turns, evaluators need side-by-side artifacts to judge which completion is better — this folder is that artifact store.

## Architecture

```
Colosseum/
├── JanColosseum/        # Early tasks (50 files)
├── StemColosseum/       # STEM focus (104 files)
├── The Colosseum V2/    # Largest branch (358 files)
├── V2/                  # Refined tasks incl. TradingBot (82 files)
└── OldColoessum/        # Legacy stubs (2 files)
```

### Per-task structure

```
<TaskName>/Turn<N>/
  CompletionA/
    CompletionA.py
  CompletionB/
    CompletionB.py
```

Some tasks use typos: `CompleitonA`, `completionA`.

## Branches

| Branch | Notable tasks |
|--------|---------------|
| JanColosseum | Annotations, DoctorData, GridPuzzle, MonteCarlo, PriorityQueue |
| StemColosseum | GameData, Hamiltonian, LLaMA, TorchSimulate, WordErrorRate |
| The Colosseum V2 | Weeks 1–7; Swift completions in Week7 |
| V2 | TradingBot, bankProcessing, NetworkGraph, refactorDRY |

## Inputs / outputs

| | |
|-|-|
| **Input** | Model-generated code per turn (committed as files) |
| **Output** | Two variants for human comparison |
| **Automated output** | None (no in-repo preference scorer) |

## Dependencies

Per-completion — typically numpy, matplotlib, pandas. TradingBot has full `requirements.txt`.

## Usage

```bash
# Compare two completions manually
diff Colosseum/JanColosseum/Annotations/Turn1/CompletionA/CompletionA.py \
     Colosseum/JanColosseum/Annotations/Turn1/CompletionB/CompletionB.py

# List Colosseum tasks
python scripts/list_tasks.py --track colosseum
```

## Design decisions

| Decision | Why |
|----------|-----|
| Turn-based folders | Mirrors multi-turn chat sessions |
| A/B not A/B/C | Binary preference standard for RLHF datasets |
| Duplicate naming (CompletionA.py inside CompletionA/) | Matches eval platform export conventions |

## Limitations

- No manifest of prompts (only code artifacts)
- No automated diff scoring
- Filename inconsistencies

## Future improvements

- Export script: Colosseum → JSONL preference format
- Normalize Completion folder naming
- Add prompt.json per turn if available
