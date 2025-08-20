#ideal_completion.py

import random
import matplotlib.pyplot as plt
class Transaction:
    def __init__(self, txn_id, txn_type, direction, rate, amount):
        self.txn_id = txn_id
        self.txn_type = txn_type
        self.direction = direction
        self.rate = rate
        self.amount = amount

class TradeLedger:
    def __init__(self):
        self.transactions = []
        self.ppu_calculator = PPUCalculator()

    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        if transaction.rate is not None:
            self.ppu_calculator.refresh(transaction.rate, transaction.amount)

    def print_empty_ledger(self):
        if not self.transactions:
            print("Trade Ledger is empty.")
        else:
            print("Trade Ledger has transactions.")

    def show_tier_I_prices(self):
        buys = [txn for txn in self.transactions if txn.direction == "acquire" and txn.rate is not None]
        sells = [txn for txn in self.transactions if txn.direction == "offload" and txn.rate is not None]
        if buys and sells:
            top_buy = max(buys, key=lambda x: x.rate)
            top_sell = min(sells, key=lambda x: x.rate)
            print(f"Tier-I Prices: Top Acquire: {top_buy.rate:.2f} / Top Offload: {top_sell.rate:.2f}")
        else:
            print("Insufficient data for Tier-I prices.")

    def show_tier_II_prices(self, num=5):
        buys = sorted([txn for txn in self.transactions if txn.direction == "acquire" and txn.rate is not None],
                      key=lambda x: x.rate, reverse=True)[:num]
        sells = sorted([txn for txn in self.transactions if txn.direction == "offload" and txn.rate is not None],
                      key=lambda x: x.rate)[:num]

        print(f"Tier-II Prices (Top {num} transactions):")
        print("Acquires:")
        for buy in buys:
            print(f"Rate: {buy.rate:.2f}, Amount: {buy.amount}")
        print("Offloads:")
        for sell in sells:
            print(f"Rate: {sell.rate:.2f}, Amount: {sell.amount}")

    def show_tier_III_prices(self):
        buys = sorted([txn for txn in self.transactions if txn.direction == "acquire" and txn.rate is not None],
                      key=lambda x: x.rate, reverse=True)
        sells = sorted([txn for txn in self.transactions if txn.direction == "offload" and txn.rate is not None],
                      key=lambda x: x.rate)

        print("Tier-III Prices (Full transaction depth):")
        print("Acquires:")
        for buy in buys:
            print(f"Rate: {buy.rate:.2f}, Amount: {buy.amount}")
        print("Offloads:")
        for sell in sells:
            print(f"Rate: {sell.rate:.2f}, Amount: {sell.amount}")  # Fixed: sell.amount instead of buy.amount

    def monitor_stop_limits(self, live_rate):
        executed_transactions = []
        for txn in self.transactions[:]:  # Create a copy of the list to iterate over
            if txn.rate is None:
                continue  # Skip market transactions that don't have a rate
            if (txn.direction == "offload" and live_rate <= txn.rate) or \
               (txn.direction == "acquire" and live_rate >= txn.rate):
                print(f"Stop-limit triggered for {txn.direction} transaction at {txn.rate:.2f}!")
                executed_transactions.append(txn)
                self.transactions.remove(txn)
        return executed_transactions


class PPUCalculator:
    def __init__(self):
        self.total_rate_volume = 0
        self.total_units = 0

    def refresh(self, rate, units):
        self.total_rate_volume += rate * units
        self.total_units += units

    def fetch_ppu(self):
        if self.total_units == 0:
            return None
        return self.total_rate_volume / self.total_units

def simulate_transactions(trade_ledger, num_transactions=10):
    for i in range(num_transactions):
        txn_id = len(trade_ledger.transactions) + 1
        txn_type = random.choice(['market', 'cap'])
        direction = random.choice(['acquire', 'offload'])
        rate = random.uniform(90, 110) if txn_type == 'cap' else None
        amount = random.randint(1, 100)
        
        transaction = Transaction(txn_id, txn_type, direction, rate, amount)
        trade_ledger.add_transaction(transaction)
        
        rate_str = f"{rate:.2f}" if rate is not None else "N/A"
        print(f"Added transaction: ID {txn_id}, Type {txn_type}, Direction {direction}, "
              f"Rate {rate_str}, Amount {amount}")

def visualize_ledger(trade_ledger):
    acquire_rates = [txn.rate for txn in trade_ledger.transactions
                     if txn.direction == 'acquire' and txn.rate is not None]
    offload_rates = [txn.rate for txn in trade_ledger.transactions
                     if txn.direction == 'offload' and txn.rate is not None]
    
    plt.figure(figsize=(10, 6))
    plt.scatter(range(len(acquire_rates)), acquire_rates, color='green', label='Acquire')
    plt.scatter(range(len(offload_rates)), offload_rates, color='red', label='Offload')
    plt.title('Trade Ledger Transactions')
    plt.xlabel('Transaction Index')
    plt.ylabel('Rate')
    plt.legend()
    plt.show()

def main_simulation():
    trade_ledger = TradeLedger()
    
    print("Initial state:")
    trade_ledger.print_empty_ledger()
    
    print("\nSimulating transactions...")
    simulate_transactions(trade_ledger, num_transactions=20)
    
    print("\nFinal state:")
    trade_ledger.print_empty_ledger()
    
    print("\nShowing Tier-I prices:")
    trade_ledger.show_tier_I_prices()
    
    print("\nShowing Tier-II prices:")
    trade_ledger.show_tier_II_prices()
    
    print("\nShowing Tier-III prices (full depth):")
    trade_ledger.show_tier_III_prices()
    
    print(f"\nCurrent PPU: {trade_ledger.ppu_calculator.fetch_ppu():.2f}")
    
    print("\nSimulating stop limit monitoring...")
    live_rate = random.uniform(90, 110)
    print(f"Current live rate: {live_rate:.2f}")
    executed_transactions = trade_ledger.monitor_stop_limits(live_rate)
    print(f"Number of executed transactions: {len(executed_transactions)}")
    
    visualize_ledger(trade_ledger)

if __name__ == "__main__":
    main_simulation()