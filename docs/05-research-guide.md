# Research Guide

## Scope

This document covers **algorithms actually implemented** in the repository. There is **no RLHF, PPO, or DPO training math** here.

## Classical optimization

### A* / heap-based search

**Where:** `Month5/Reviews3/8Puzzle/`, Lagrangian relaxation tasks

**Objective:** Minimize path cost on discrete state graphs.

**Implementation:** `heapq.heappop` priority queues — standard informed search, not policy gradients.

### Lagrangian relaxation

**Where:** `Month5/Reviews4/Lagrangian Relaxation/`

**Math:** Relax combinatorial constraints via Lagrange multipliers; iteratively update dual variables.

**Use in repo:** Shortest path / assignment style problems.

## Evolutionary algorithm (not RL)

**Where:** `Months/Month6/multi_turn2/genetic/ideal_completion.py`

**Fitness:**

```
fitness = total_metal + airflow_diff * 1000 + violations * 10000
```

**Operators:** Selection, crossover, mutation on ductwork routing individuals.

**Distinction from RL:** No policy network, no environment step reward accumulation, no value function.

## Monte Carlo simulation

**Where:** `Months/Month6/Review_multi-turn/Batch1/Monte-Carlo/`

**Math:** Sample photon paths; compare empirical absorption to Beer-Lambert law:

```
theoretical_fraction = exp(-μ_a * z) * (1 - exp(-μ_a * Δz))
```

**Not** RL Monte Carlo policy evaluation.

## Supervised machine learning

### Semi-supervised Keras model

**Where:** `Months/Month6/multi_turn2/Model/`

- `ModifiedFlySmote` — custom SMOTE oversampling
- `SemiSupervisedModel` — federated-style client loops with `model.fit()`
- Optimizer: `Adam`; loss: categorical crossentropy (classification)

### PyTorch small NN

**Where:** `Month6/Review_multi-turn/Batch2/decision/`

Standard supervised training loop.

### CRF (pycrfsuite)

**Where:** `Month6/Review_multi-turn/Batch2/CRF/`

Sequence labeling — `pycrfsuite.Trainer`, not RL trainer.

## Financial mathematics

### BondAnalyzer

**Where:** `Months/Month6/multi_turn2/BondAnalyzer/ideal_completion.py`

- Bootstrap zero rates from bond prices
- Forward rates, swap rates
- Arbitrage detection across tenor segments

Uses `scipy.optimize.minimize`, `LinearRegression`.

## LLM inference (not training)

### OpenAI API

```python
client.chat.completions.create(model="gpt-3.5-turbo", messages=[...])
```

### LangChain Chroma

Vector similarity search over embeddings — retrieval, not fine-tuning.

## If you need RLHF math

Use external frameworks (TRL, OpenRLHF, etc.) and optionally export:

- Colosseum A/B pairs → preference dataset
- `tests.py` pass/fail → rule-based reward signal

This repo provides **evaluation substrate**, not the optimization loop.
