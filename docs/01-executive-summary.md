# Executive Summary

## Repository identity

**OpenAI-RLHF** is a **coding evaluation task archive**, not an OpenAI reinforcement-learning or RLHF training codebase.

| Attribute | Value |
|-----------|-------|
| **Primary purpose** | Verify LLM-generated code; collect A/B completion preference pairs |
| **Scale** | ~1,450 Python files, ~1,490 total source files |
| **License** | MIT (Copyright 2025 Ayush Rai) |
| **Git history** | 3 commits — archive, not active framework development |
| **Maturity** | Task-level complete; repo-level minimal (now improved with docs/scripts) |

## Two evaluation tracks

### Months — automated correctness

- **Pattern:** `ideal_completion.py` (gold) + `tests.py` (unittest)
- **Verdict:** Pass/fail via assertions
- **~186** tasks with `ideal_completion.py`

### Colosseum — human preference

- **Pattern:** `TurnN/CompletionA/` vs `CompletionB/`
- **Verdict:** Human labeler chooses preferred completion
- **~200+** task folders with A/B pairs

## What this repository is NOT

Evidence from full-tree grep (`PPO`, `RLHF`, `DPO`, `reward_model`, `policy_gradient`): **no matches** except the README title.

- No policy optimization (PPO, TRPO, SAC, DQN)
- No preference training (DPO, IPO, ORPO, GRPO)
- No reward models or rollout collectors
- No Gym/RL environments
- No Triton kernels (`triton/` is empty)

## Confidence

| Conclusion | Confidence |
|------------|------------|
| Eval archive, not RL trainer | 99% |
| Colosseum = preference labeling substrate | 95% |
| Could be repurposed as RLHF *dataset* with external trainer | 80% |

## Next steps for new readers

1. [Repository Overview](02-repository-overview.md)
2. [Architecture Guide](03-architecture-guide.md)
3. [Developer Onboarding](11-developer-onboarding.md)
