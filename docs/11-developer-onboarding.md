# Developer Onboarding Guide

## Week 1 plan

### Day 1 — Orientation (2 hours)

1. Read [Executive Summary](01-executive-summary.md)
2. Clone repo, run:
   ```bash
   python scripts/generate_task_manifest.py
   python scripts/validate_repo.py
   python scripts/list_tasks.py --limit 20
   ```
3. Accept: **not an RL framework**

### Day 2 — Run eval tasks (2 hours)

```bash
cd Months/Month6/multi_turn2/BondAnalyzer && python tests.py
cd ../Flask && pip install fpdf reportlab python-docx odfpy && python tests.py
```

Read `ideal_completion.py` and `tests.py` side by side.

### Day 3 — Colosseum (1 hour)

Explore:

```
Colosseum/JanColosseum/Annotations/Turn1/CompletionA/
Colosseum/V2/Week1/TradingBot/
```

Read [projects/colosseum.md](projects/colosseum.md) and [projects/trading-bot.md](projects/trading-bot.md).

### Day 4 — Domain deep dive (3 hours)

Pick one domain from `TASKS.json`:

| Interest | Start path |
|----------|------------|
| Finance | `Months/Month6/multi_turn2/BondAnalyzer` |
| ML | `Months/Month6/multi_turn2/Model` |
| Web | `Months/Month6/Review_multi-turn/Batch3` |
| LLM APIs | `Months/Month5/Reviews4/OpenAI_API` |
| Algorithms | `Months/Month5/Reviews3/8Puzzle` |

### Day 5 — Tooling (2 hours)

- Modify `scripts/list_tasks.py` filters
- Run `python scripts/run_tests.py --month Month7 --limit 5`
- Read [Engineering Guide](06-engineering-guide.md)

## Key files to know

| File | Purpose |
|------|---------|
| `TASKS.json` | Task index |
| `scripts/generate_task_manifest.py` | Regenerate index |
| `scripts/run_tests.py` | Batch test runner |
| `docs/03-architecture-guide.md` | System design |
| `CONTRIBUTING.md` | Contribution rules |

## Common pitfalls

1. **Wrong cwd** — always run `tests.py` from task directory
2. **Missing deps** — no universal requirements.txt for all tasks
3. **Import from working_ideal_completion** — check `tests.py` imports first
4. **Selenium without driver** — install chromedriver for web tasks
5. **Assuming RLHF** — name is historical/misleading

## Suggested first contributions

1. Fix filename typos (`tersts.py` → `tests.py`)
2. Add task-local `README.md` for complex tasks (TradingBot)
3. Extend `generate_task_manifest.py` with dependency hints
4. Add GitHub Actions smoke test on Month7 tasks (small, few deps)
5. Export Colosseum pairs to JSONL for preference research

## Getting help

- Check [Evaluation Guide](08-evaluation-guide.md) for test failures
- Check [Dependency Guide](10-dependency-guide.md) for pip packages
- Run `python scripts/validate_repo.py --json` for structure issues

## Code walkthrough order

1. `Months/Month6/multi_turn2/BondAnalyzer/` — clean OOP + tests
2. `Months/Month6/multi_turn2/Flask/` — file I/O + multi-format
3. `Months/Month6/multi_turn2/Model/` — ML + test variant pattern
4. `Colosseum/V2/Week1/TradingBot/CompletionB/bot.py` — largest app
5. `Months/Month5/Reviews4/OpenAI_API/` — minimal API wrapper
