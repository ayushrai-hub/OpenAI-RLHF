# Documentation Index

Complete reverse-engineering documentation for the OpenAI-RLHF evaluation archive.

## Core documents

| # | Document | Description |
|---|----------|-------------|
| 1 | [Executive Summary](01-executive-summary.md) | What this repo is and is not |
| 2 | [Repository Overview](02-repository-overview.md) | Scope, users, maturity |
| 3 | [Architecture Guide](03-architecture-guide.md) | Design, diagrams, data flow |
| 4 | [Beginner's Guide](04-beginners-guide.md) | Python-only prerequisite |
| 5 | [Research Guide](05-research-guide.md) | Algorithms (non-RL) |
| 6 | [Engineering Guide](06-engineering-guide.md) | Patterns, tooling |
| 7 | [Training Guide](07-training-guide.md) | Supervised ML tasks only |
| 8 | [Evaluation Guide](08-evaluation-guide.md) | Running tests |
| 9 | [Configuration Guide](09-configuration-guide.md) | YAML, env vars |
| 10 | [Dependency Guide](10-dependency-guide.md) | Packages by domain |
| 11 | [Developer Onboarding](11-developer-onboarding.md) | First-week plan |
| 12 | [API Reference](12-api-reference.md) | Key interfaces |

## Project subsystems

| Document | Subsystem |
|----------|-----------|
| [Colosseum](projects/colosseum.md) | A/B completion pairs |
| [Months](projects/months.md) | Eval corpus |
| [TradingBot](projects/trading-bot.md) | Binance trading bot |

## Other

| Document | Description |
|----------|-------------|
| [Recommendations](13-recommendations.md) | Future work, CI, refactoring |

## Tooling

```bash
python scripts/generate_task_manifest.py   # → TASKS.json
python scripts/list_tasks.py
python scripts/run_tests.py
python scripts/validate_repo.py
```
