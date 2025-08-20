class Transaction:
    def __init__(self, txn_id: int, txn_type: str, direction: str, rate: float, amount: int):
        self.txn_id = txn_id
        self.txn_type = txn_type
        self.direction = direction
        self.rate = rate
        self.amount = amount

    def __repr__(self):
        return f"Transaction({self.txn_id}, {self.txn_type}, {self.direction}, {self.rate}, {self.amount})"


class PPUCalculator:
    def __init__(self):
        self.total_value = 0.0
        self.total_units = 0

    def refresh(self, rate: float, units: int) -> None:
        if rate is None or units is None:
            return
        self.total_value += rate * units
        self.total_units += units

    def fetch_ppu(self):
        if self.total_units == 0:
            return None
        return self.total_value / self.total_units


class TradeLedger:
    def __init__(self):
        self.transactions = []
        self.ppu_calculator = PPUCalculator()

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)
        self.ppu_calculator.refresh(transaction.rate, transaction.amount)

    def print_empty_ledger(self) -> None:
        if not self.transactions:
            print("Trade Ledger is empty.")
        else:
            print("Trade Ledger has transactions.")

    def show_tier_I_prices(self) -> None:
        acquire_rates = [t.rate for t in self.transactions if t.direction == "acquire" and t.rate is not None]
        offload_rates = [t.rate for t in self.transactions if t.direction == "offload" and t.rate is not None]
        top_acquire = max(acquire_rates) if acquire_rates else None
        top_offload = min(offload_rates) if offload_rates else None
        parts = []
        if top_acquire is not None:
            parts.append(f"Top Acquire: {top_acquire:.2f}")
        if top_offload is not None:
            parts.append(f"Top Offload: {top_offload:.2f}")
        joined = " / ".join(parts)
        print("Tier-I Prices: " + joined)

    def show_tier_II_prices(self, num: int = 5) -> None:
        sorted_txns = sorted(self.transactions, key=lambda t: (t.rate if t.rate is not None else float("-inf")), reverse=True)
        top = sorted_txns[:num]
        print(f"Tier-II Prices (Top {num} transactions):")
        for t in top:
            rate_str = f"{t.rate:.2f}" if t.rate is not None else "None"
            print(f"Rate: {rate_str}, Amount: {t.amount}")

    def show_tier_III_prices(self) -> None:
        print("Tier-III Prices (Full transaction depth):")
        for t in self.transactions:
            rate_str = f"{t.rate:.2f}" if t.rate is not None else "None"
            print(f"Rate: {rate_str}, Amount: {t.amount}")

    def monitor_stop_limits(self, live_rate: float) -> list:
        stops = []
        for t in self.transactions:
            if t.rate is None:
                continue
            if t.direction == "acquire" and live_rate < t.rate:
                stops.append(t)
            if t.direction == "offload" and live_rate > t.rate:
                stops.append(t)
        return stops


def simulate_transactions(trade_ledger: TradeLedger, num_transactions: int = 10) -> None:
    for i in range(1, num_transactions + 1):
        txn_type = "market" if i % 2 == 0 else "cap"
        direction = "acquire" if i % 2 != 0 else "offload"
        rate = i * 100.0
        amount = i * 50
        txn = Transaction(txn_id=i, txn_type=txn_type, direction=direction, rate=rate, amount=amount)
        trade_ledger.add_transaction(txn)
        print(f"Added transaction: ID {txn.txn_id}, Type {txn.txn_type}, Direction {txn.direction}, Rate {txn.rate:.2f}, Amount {txn.amount}")


def visualize_ledger(trade_ledger: TradeLedger) -> None:
    for t in trade_ledger.transactions:
        rate_str = f"{t.rate:.2f}" if t.rate is not None else "None"
        print(f"ID: {t.txn_id}, Type: {t.txn_type}, Direction: {t.direction}, Rate: {rate_str}, Amount: {t.amount}")


def main_simulation() -> None:
    ledger = TradeLedger()
    simulate_transactions(ledger, 5)
    visualize_ledger(ledger)
    ledger.print_empty_ledger()
    ledger.show_tier_I_prices()
    ledger.show_tier_II_prices(3)
    ledger.show_tier_III_prices()
    ppu = ledger.ppu_calculator.fetch_ppu()
    if ppu is None:
        print("PPU: None")
    else:
        print("PPU:", ppu)
    stops = ledger.monitor_stop_limits(live_rate=25.0)
    print("Stop limits triggered:", stops)