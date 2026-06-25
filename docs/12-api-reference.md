# API Reference

There is **no unified public API**. This documents important **per-task interfaces**.

---

## `BondAnalyzer`

**Path:** `Months/Month6/multi_turn2/BondAnalyzer/ideal_completion.py`

```python
class BondAnalyzer:
    def __init__(self, libor_3m: float, libor_6m: float, bond_prices: list, scenario: str = 'base')
    def generate_payment_times(self) -> list
    def build_cashflow_matrix(self) -> np.ndarray
    def check_arbitrage(self, zero_rates: list) -> list
    def analyze(self) -> tuple  # zero, forward, swap, arbitrage
```

**Used by:** `tests.py` — validates yield curve math and arbitrage structure.

---

## `has_plagiarism`

**Path:** `Months/Month6/multi_turn2/Flask/ideal_completion.py`

```python
def has_plagiarism(file_path: str, reference_text: str, threshold: float) -> bool
```

Detects text overlap in PDF, DOCX, ODT files.

---

## `ModifiedFlySmote` / `SemiSupervisedModel`

**Path:** `Months/Month6/multi_turn2/Model/working_ideal_completion.py`

```python
class ModifiedFlySmote:
    def __init__(self, X_train, Y_train)
    def find_nearest_neighbors(self, data, prediction, k) -> list
    def generate_synthetic_data(self, minority_val, k, ratio) -> tuple

class SemiSupervisedModel:
    def __init__(self, train_set, test_set, encoder, clients_amount=10, iterations=5, epochs=10)
    def update_distributed_data(self, ...) -> ...
    def train(self) -> ...
```

**Tests import from:** `working_ideal_completion`, not `ideal_completion`.

---

## Genetic algorithm functions

**Path:** `Months/Month6/multi_turn2/genetic/ideal_completion.py`

```python
def initialize_population(pop_size: int, room_info: dict) -> list
def calculate_fitness(individual: dict) -> int
def crossover(parent1, parent2) -> tuple
def mutate(individual) -> list
def visualize_ductwork(solution: dict) -> Figure
```

**Helpers in:** `utils.py` — `compute_total_metal`, `evaluate_violations`, etc.

---

## `get_chatgpt_response`

**Path:** `Months/Month5/Reviews4/OpenAI_API/ideal_completion.py`

```python
def get_chatgpt_response(prompt: str) -> str
```

Requires `OPENAI_API_KEY` environment variable.

---

## `get_docs`

**Path:** `Months/Month5/Reviews4/LangChain/ideal_completion.py`

```python
def get_docs(collection_name, persist_directory, embeddings, query, k) -> list
```

Chroma vector similarity search.

---

## `TradingBot`

**Path:** `Colosseum/V2/Week1/TradingBot/CompletionB/bot.py`

```python
class TradingBot:
    def __init__(self)
    def load_config(self) -> None
    def setup_exchange(self) -> None
    def setup_strategies(self) -> None
    def run(self) -> None  # main loop
```

**Strategies:**

- `strategies/moving_average.py` — `MovingAverageStrategy`
- `strategies/rsi_strategy.py` — `RSIStrategy`
- `strategies/base_strategy.py` — base class

**Utils:**

- `utils/database.py` — `Database`
- `utils/telegram_notifications.py` — `TelegramNotifier`

---

## Django models (stub)

**Path:** `test/test_app/models.py`

```python
class Task(models.Model):
    name = models.CharField(max_length=255)
    comments = models.TextField(blank=True, null=True)

class Attachment(models.Model):
    task = models.ForeignKey(Task, related_name='attachments', on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='attachments/')
```

---

## Tooling CLI

### `scripts/generate_task_manifest.py`

```bash
python scripts/generate_task_manifest.py [-o TASKS.json]
```

### `scripts/list_tasks.py`

```bash
python scripts/list_tasks.py [--track months|colosseum|all] [--domain DOMAIN] [--month Month6]
```

### `scripts/run_tests.py`

```bash
python scripts/run_tests.py [--path PATH] [--month Month6] [--limit N] [--timeout SEC]
```

### `scripts/validate_repo.py`

```bash
python scripts/validate_repo.py [--json]
```
