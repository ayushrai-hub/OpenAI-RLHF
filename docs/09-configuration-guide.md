# Configuration Guide

## Repo-level configuration

**None.** No root `config.yaml`, Hydra, or OmegaConf.

## TradingBot configuration

**Path:** `Colosseum/V2/Week1/TradingBot/CompletionB/config/config.yaml`

### `exchange`

| Key | Default | Description |
|-----|---------|-------------|
| `name` | `binance` | ccxt exchange id |
| `testnet` | `false` | Sandbox mode |
| `api_key` | `${BINANCE_API_KEY}` | Resolved from env |
| `api_secret` | `${BINANCE_API_SECRET}` | Resolved from env |

### `trading`

| Key | Default | Description |
|-----|---------|-------------|
| `symbols` | BTC/USDT, ETH/USDT | Trading pairs |
| `base_order_size_usdt` | 100 | Order size |
| `max_open_trades` | 3 | Position limit |
| `stop_loss_percentage` | 2.5 | Stop loss % |
| `take_profit_percentage` | 5 | Take profit % |
| `position_size_percentage` | 2 | Position sizing |

### `strategies.moving_average`

| Key | Default | Description |
|-----|---------|-------------|
| `enabled` | true | Toggle strategy |
| `short_window` | 20 | Short MA period |
| `long_window` | 50 | Long MA period |

### `strategies.rsi`

| Key | Default | Description |
|-----|---------|-------------|
| `enabled` | true | Toggle strategy |
| `period` | 14 | RSI period |
| `overbought` | 70 | Sell signal threshold |
| `oversold` | 30 | Buy signal threshold |

### `telegram`

| Key | Description |
|-----|-------------|
| `enabled` | Send trade notifications |
| `bot_token` | From `TELEGRAM_BOT_TOKEN` env |
| `chat_id` | From `TELEGRAM_CHAT_ID` env |

### `database`

| Key | Default | Description |
|-----|---------|-------------|
| `url` | `sqlite:///trading_bot.db` | SQLAlchemy URL |

### Environment setup

```bash
export BINANCE_API_KEY=...
export BINANCE_API_SECRET=...
export TELEGRAM_BOT_TOKEN=...
export TELEGRAM_CHAT_ID=...
```

Loaded via `python-dotenv` in `bot.py`.

## Django settings (`test/test_project/settings.py`)

| Setting | Value |
|---------|-------|
| Database | SQLite in-memory |
| `INSTALLED_APPS` | Includes `test_app` |

Not runnable without adding `manage.py`.

## Task-level configuration

Some tasks use argparse CLI:

- `Months/Month4/EDIT/config/ideal.py`

Most tasks hardcode parameters in `ideal_completion.py`.

## CLI arguments (tooling)

| Script | Args |
|--------|------|
| `generate_task_manifest.py` | `-o OUTPUT` |
| `list_tasks.py` | `--track`, `--domain`, `--month`, `--has-tests` |
| `run_tests.py` | `--path`, `--month`, `--limit`, `--timeout`, `--fail-fast` |
| `validate_repo.py` | `--json` |

## Overrides

No config inheritance. Edit YAML or Python literals directly.
