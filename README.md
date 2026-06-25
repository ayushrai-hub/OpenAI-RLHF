# OpenAI-RLHF

Archive of **coding evaluation tasks** and **A/B completion comparison artifacts** for assessing LLM-generated code.

> **Important:** Despite the name, this repository does **not** contain RLHF, PPO, DPO, or reinforcement-learning training pipelines. See [docs/01-executive-summary.md](docs/01-executive-summary.md).

## What is in this repo?

| Track | Path | Pattern | Purpose |
|-------|------|---------|---------|
| **Months** | `Months/` | `ideal_completion.py` + `tests.py` | Gold solution + automated unittest verification |
| **Colosseum** | `Colosseum/` | `TurnN/CompletionA|B/` | Multi-turn A/B model completion pairs for preference labeling |
| **Test stub** | `test/` | Django models | Minimal scaffold |
| **Triton** | `triton/` | *(empty)* | Placeholder |

~1,450 Python files across finance, ML, algorithms, web (Selenium), Django, Flask, and more.

## Quick start

```bash
# Generate task index
python scripts/generate_task_manifest.py

# List all Months tasks with tests
python scripts/list_tasks.py --track months --has-tests

# Run a single eval task
cd Months/Month6/multi_turn2/BondAnalyzer
python tests.py

# Run many tasks (may require per-task dependencies)
python scripts/run_tests.py --month Month6 --limit 5

# Validate repo structure
python scripts/validate_repo.py
```

## Documentation

| Document | Description |
|----------|-------------|
| [Executive Summary](docs/01-executive-summary.md) | What this repo is and is not |
| [Repository Overview](docs/02-repository-overview.md) | Scope, maturity, users |
| [Architecture Guide](docs/03-architecture-guide.md) | System design and diagrams |
| [Beginner's Guide](docs/04-beginners-guide.md) | Python-only prerequisite |
| [Research Guide](docs/05-research-guide.md) | Algorithms found (non-RL) |
| [Engineering Guide](docs/06-engineering-guide.md) | Patterns and conventions |
| [Training Guide](docs/07-training-guide.md) | Supervised ML tasks (no RLHF trainer) |
| [Evaluation Guide](docs/08-evaluation-guide.md) | Running and interpreting tests |
| [Configuration Guide](docs/09-configuration-guide.md) | YAML/env config (TradingBot) |
| [Dependency Guide](docs/10-dependency-guide.md) | Libraries by domain |
| [Developer Onboarding](docs/11-developer-onboarding.md) | First-week guide |
| [API Reference](docs/12-api-reference.md) | Key per-task interfaces |
| [Colosseum](docs/projects/colosseum.md) | A/B completion subsystem |
| [Months](docs/projects/months.md) | Eval corpus subsystem |
| [TradingBot](docs/projects/trading-bot.md) | Most complete mini-app |

## Project structure

```
OpenAI-RLHF/
├── Colosseum/          # A/B multi-turn completions (~596 files)
├── Months/             # ideal_completion + tests (~886 files)
├── test/               # Django stub
├── triton/             # Empty placeholder
├── docs/               # Documentation (this index)
├── scripts/            # Manifest, test runner, validation
├── TASKS.json          # Generated task manifest
├── requirements-dev.txt
├── CONTRIBUTING.md
└── LICENSE             # MIT
```

## Notable tasks

| Task | Path | Domain |
|------|------|--------|
| TradingBot | `Colosseum/V2/Week1/TradingBot/` | Binance bot (ccxt) |
| BondAnalyzer | `Months/Month6/multi_turn2/BondAnalyzer/` | Fixed income |
| Model | `Months/Month6/multi_turn2/Model/` | Semi-supervised Keras |
| OpenAI API | `Months/Month5/Reviews4/OpenAI_API/` | GPT-3.5 wrapper |
| LangChain | `Months/Month5/Reviews4/LangChain/` | Chroma vector search |

## Dependencies

There is **no root runtime requirements file** — dependencies are per-task. For tooling:

```bash
pip install -r requirements-dev.txt
```

Task-specific example: `Colosseum/V2/Week1/TradingBot/CompletionB/requirements.txt`

## FAQ

**Can I train RLHF here?** No. There is no trainer, reward model, or preference optimizer.

**What is Colosseum?** Competing code completions (A vs B) across conversational turns for human preference labeling.

**Why is `triton/` empty?** Placeholder; no GPU kernel code was committed.

## License

MIT — Copyright 2025 Ayush Rai. See [LICENSE](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
