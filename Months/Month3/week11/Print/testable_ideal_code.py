
import random


class Transaction:
    """
    Class representing a transaction (either market or cap) in the trade ledger.
    """
    def __init__(self, txn_id, txn_type, direction, rate, amount):
        """
        Initialize the transaction.

        :param txn_id: Unique ID for the transaction.
        :param txn_type: Type of the transaction ('market' or 'cap').
        :param direction: 'acquire' or 'offload'.
        :param rate: Rate of the transaction (None for market transactions).
        :param amount: Amount of commodities in the transaction.
        """
        self.txn_id = txn_id
        self.txn_type = txn_type
        self.direction = direction
        self.rate = rate
        self.amount = amount


class TradeLedger:
    """
    Class representing the trade ledger that holds all transactions and price per unit.
    """
    def __init__(self):
        """
        Initialize an empty trade ledger.
        """
        self.transactions = []
        self.ppu_calculator = PPUCalculator()

    def add_transaction(self, transaction):
        """
        Add a transaction to the trade ledger.

        :param transaction: Transaction to be added.
        """
        self.transactions.append(transaction)

    def print_empty_ledger(self):
        """
        Print a message indicating that the trade ledger is empty.
        """
        if not self.transactions:
            print("Trade Ledger is empty.")
        else:
            print("Trade Ledger has transactions.")

    def show_tier_I_prices(self):
        """
        Show Tier-I prices: Best acquire and offload only.
        """
        buys = [txn for txn in self.transactions if txn.direction == "acquire" and txn.rate is not None]
        sells = [txn for txn in self.transactions if txn.direction == "offload" and txn.rate is not None]
        if buys and sells:
            top_buy = max(buys, key=lambda x: x.rate)
            top_sell = min(sells, key=lambda x: x.rate)
            print(f"Tier-I Prices: Top Acquire: {top_buy.rate} / Top Offload: {top_sell.rate}")

    def show_tier_II_prices(self, num=5):
        """
        Show Tier-II prices: Transaction depth (acquire/offload) up to the specified depth.

        :param num: Number of transactions to display on each side.
        """
        buys = sorted([txn for txn in self.transactions if txn.direction == "acquire" and txn.rate is not None],
                      key=lambda x: x.rate, reverse=True)[:num]
        sells = sorted([txn for txn in self.transactions if txn.direction == "offload" and txn.rate is not None],
                      key=lambda x: x.rate)[:num]

        print(f"Tier-II Prices (Top {num} transactions):")
        print("Acquires:")
        for buy in buys:
            print(f"Rate: {buy.rate}, Amount: {buy.amount}")
        print("Offloads:")
        for sell in sells:
            print(f"Rate: {sell.rate}, Amount: {sell.amount}")

    def show_tier_III_prices(self):
        """
        Show Tier-III prices: Full transaction depth.
        """
        buys = sorted([txn for txn in self.transactions if txn.direction == "acquire" and txn.rate is not None],
                      key=lambda x: x.rate, reverse=True)
        sells = sorted([txn for txn in self.transactions if txn.direction == "offload" and txn.rate is not None],
                      key=lambda x: x.rate)

        print("Tier-III Prices (Full transaction depth):")
        print("Acquires:")
        for buy in buys:
            print(f"Rate: {buy.rate}, Amount: {buy.amount}")
        print("Offloads:")
        for sell in sells:
            print(f"Rate: {sell.rate}, Amount: {sell.amount}")

    def monitor_stop_limits(self, live_rate):
        """
        Monitor and execute stop-limit transactions if the live rate hits the stop points.

        :param live_rate: The current transaction rate.
        :return: List of executed stop-limit transactions.
        """
        executed_transactions = []
        for txn in self.transactions:
            if txn.rate is None:
                continue  # Skip market transactions that don't have a rate

            # Check if the live rate has triggered a stop-limit for an offload transaction
            if txn.direction == "offload" and live_rate <= txn.rate:
                print(f"Stop-limit triggered for offload transaction at {txn.rate}!")
                executed_transactions.append(txn)
                self.transactions.remove(txn)

            # Check if the live rate has triggered a stop-limit for an acquire transaction
            elif txn.direction == "acquire" and live_rate >= txn.rate:
                print(f"Stop-limit triggered for acquire transaction at {txn.rate}!")
                executed_transactions.append(txn)
                self.transactions.remove(txn)

        return executed_transactions


class PPUCalculator:
    """
    Class for calculating PPU (Price Per Unit).
    """
    def __init__(self):
        """
        Initialize with zero rate and volume.
        """
        self.total_rate_volume = 0
        self.total_units = 0

    def refresh(self, rate, units):
        """
        Refresh the PPU calculation with a new transaction.

        :param rate: Rate of the transaction.
        :param units: Amount of units.
        """
        self.total_rate_volume += rate * units
        self.total_units += units

    def fetch_ppu(self):
        """
        Fetch the current PPU.

        :return: The price per unit.
        """
        if self.total_units == 0:
            return None
        return self.total_rate_volume / self.total_units


def simulate_transactions(trade_ledger, num_transactions=10):
    """
    Simulate adding a number of transactions to the trade ledger.

    :param trade_ledger: The trade ledger to add transactions to.
    :param num_transactions: The number of transactions to simulate.
    """
    for i in range(num_transactions):
        txn_id = i + 1
        txn_type = random.choice(["market", "cap"])
        direction = random.choice(["acquire", "offload"])
        rate = round(random.uniform(10, 100), 2) if txn_type == "cap" else None
        amount = random.randint(1, 1000)
        trade_ledger.add_transaction(Transaction(txn_id, txn_type, direction, rate, amount))


def visualize_ledger(trade_ledger):
    """
    Visualize the transactions in the trade ledger.

    :param trade_ledger: The trade ledger to visualize.
    """
    print("Visualizing Ledger Transactions:")
    for txn in trade_ledger.transactions:
        print(f"ID: {txn.txn_id}, Type: {txn.txn_type}, Direction: {txn.direction}, "
              f"Rate: {txn.rate}, Amount: {txn.amount}")


def main_simulation():
    """
    Run the full simulation of transactions and ledger visualization.
    """
    ledger = TradeLedger()
    simulate_transactions(ledger)
    visualize_ledger(ledger)
    ledger.print_empty_ledger()
    ledger.show_tier_I_prices()
    ledger.show_tier_II_prices()
    ledger.show_tier_III_prices()
