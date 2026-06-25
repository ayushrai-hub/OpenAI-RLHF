# Training Guide

## RLHF / RL training

**Not applicable.** This repository contains no:

- Trainer classes
- Rollout collectors
- Reward models
- Policy optimizers
- Checkpoint managers for LLM weights

Do not expect `python train.py` or Hydra experiment configs for PPO/DPO.

## Supervised ML training (task-local)

Some tasks implement **supervised** training loops evaluated by unittest.

### Example: Semi-supervised Keras (`Months/Month6/multi_turn2/Model/`)

**Components:**

| Class/Function | Role |
|--------------|------|
| `ModifiedFlySmote` | Oversample minority class |
| `SemiSupervisedModel` | Client-based SSL iterations |
| `construct_basic_sequential_model()` | Keras `Sequential` builder |
| `consolidate_models()` | Aggregate client weights |

**Hyperparameters (in code):**

```python
clients_amount=10, iterations=5, epochs=10
```

**Optimizer:** `Adam`

**How to run:**

```bash
cd Months/Month6/multi_turn2/Model
pip install tensorflow scikit-learn pandas numpy scipy
python tests.py
```

Note: tests import from `working_ideal_completion.py`, not `ideal_completion.py`.

### Example: PyTorch NN (`Month6/Review_multi-turn/Batch2/decision/`)

Small neural network — run `tests.py` with `torch` installed.

### Example: XGBoost (`Month5/Edit_Review/XGBOOST/`)

Gradient boosting — standard `fit()` / `predict()`.

## Genetic algorithm (optimization, not NN training)

`Months/Month6/multi_turn2/genetic/` — evolutionary search for ductwork layout.

```bash
cd Months/Month6/multi_turn2/genetic
python tests.py
```

## Reproducing experiments

1. Identify task in `TASKS.json` or `python scripts/list_tasks.py --domain ml`
2. `cd` to task path
3. Install domain deps (see [Dependency Guide](10-dependency-guide.md))
4. `python tests.py`

## Changing hyperparameters

Edit literals in `ideal_completion.py` — there is no external config system for ML tasks (except TradingBot).

## Distributed training

Not implemented. `SemiSupervisedModel` **simulates** federated clients in-process.

## Logging / checkpoints

No W&B, TensorBoard, or MLflow at repo level. Keras may print training logs during test runs.

## Repurposing for RLHF (external)

| Asset | External use |
|-------|--------------|
| Colosseum A/B | DPO preference pairs |
| `tests.py` pass | Rule-based reward |
| `ideal_completion.py` | Expert demonstrations (BC) |

Build export scripts separately — not included yet.
