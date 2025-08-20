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
        # Skip None rates
        if rate is None or units is None:
            return
        self.total_value += rate * units
        self.total_units += units

    def fetch_ppu(self) -> float:
        if self.total_units == 0:
            return None
        return self.total_value / self.total_units


class TradeLedger:
    def __init__(self):
        self.transactions = []
        self.ppu_calculator = PPUCalculator()

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)
        # update ppu, skip if rate is None
        self.ppu_calculator.refresh(transaction.rate, transaction.amount)

    def print_empty_ledger(self) -> None:
        if not self.transactions:
            print("Ledger is empty")
        else:
            print("Ledger has transactions")

    def show_tier_I_prices(self) -> None:
        rates = []
        for t in self.transactions[:3]:
            if t.rate is not None:
                rates.append(f"{t.rate:.2f}")
            else:
                rates.append("None")
        print("Tier I Prices: " + ", ".join(rates))

    def show_tier_II_prices(self, num: int = 5) -> None:
        rates = []
        for t in self.transactions[:num]:
            if t.rate is not None:
                rates.append(f"{t.rate:.2f}")
            else:
                rates.append("None")
        print("Tier II Prices: " + ", ".join(rates))

    def show_tier_III_prices(self) -> None:
        rates = []
        for t in self.transactions:
            if t.rate is not None:
                rates.append(f"{t.rate:.2f}")
            else:
                rates.append("None")
        print("Tier III Prices: " + ", ".join(rates))

    def monitor_stop_limits(self, live_rate: float) -> list:
        stops = []
        for t in self.transactions:
            # skip if t.rate is None
            if t.rate is None:
                continue
            # Example logic
            if t.direction == "acquire" and live_rate < t.rate:
                stops.append(t)
            if t.direction == "offload" and live_rate > t.rate:
                stops.append(t)
        return stops


def simulate_transactions(trade_ledger: TradeLedger, num_transactions: int = 10) -> None:
    for i in range(1, num_transactions + 1):
        txn_type = "market" if i % 2 == 0 else "cap"
        direction = "acquire" if i % 2 == 0 else "offload"
        rate = i * 10.0
        amount = (i * 5)
        txn = Transaction(txn_id=i, txn_type=txn_type, direction=direction, rate=rate, amount=amount)
        trade_ledger.add_transaction(txn)
        # Logging
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
    # Print ppu, check None
    if ppu is None:
        print("PPU: None")
    else:
        print("PPU:", ppu)
    stops = ledger.monitor_stop_limits(live_rate=25.0)
    print("Stop limits triggered:", stops)