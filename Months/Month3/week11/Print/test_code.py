import unittest
from unittest.mock import patch
import io
from testable_ideal_code import Transaction, TradeLedger, PPUCalculator, simulate_transactions

class TestTradeLedger(unittest.TestCase):

    def setUp(self):
        self.ledger = TradeLedger()
        self.sample_transactions = [
            Transaction(1, 'cap', 'acquire', 100, 50),
            Transaction(2, 'cap', 'offload', 105, 30),
            Transaction(3, 'market', 'acquire', None, 40),
            Transaction(4, 'cap', 'acquire', 102, 20),
            Transaction(5, 'cap', 'offload', 103, 25),
        ]
        for transaction in self.sample_transactions:
            self.ledger.add_transaction(transaction)

    # This tests if a transaction is currently added to the ledger.
    def test_add_transaction(self):
        initial_count = len(self.ledger.transactions)
        new_transaction = Transaction(6, 'cap', 'acquire', 101, 10)
        self.ledger.add_transaction(new_transaction)
        self.assertEqual(len(self.ledger.transactions), initial_count + 1)
        self.assertIn(new_transaction, self.ledger.transactions)

    # This tests if the print_empty_ledger method correctly identifies and reports empty and non-empty ledgers.
    def test_print_empty_ledger(self):
        empty_ledger = TradeLedger()
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            empty_ledger.print_empty_ledger()
            self.assertEqual(fake_out.getvalue().strip(), "Trade Ledger is empty.")

        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            self.ledger.print_empty_ledger()
            self.assertEqual(fake_out.getvalue().strip(), "Trade Ledger has transactions.")

    # This tests if the show_tier_I_prices method correctly displays the top acquire and offload prices.
    def test_show_tier_I_prices(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            self.ledger.show_tier_I_prices()
            output = fake_out.getvalue().strip()
            self.assertIn("Tier-I Prices: Top Acquire: 102.00 / Top Offload: 103.00", output)

    # This tests if the show_tier_II_prices method correctly displays a specified number of top transactions
    def test_show_tier_II_prices(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            self.ledger.show_tier_II_prices(num=2)
            output = fake_out.getvalue().strip()
            self.assertIn("Tier-II Prices (Top 2 transactions):", output)
            self.assertIn("Rate: 102.00, Amount: 20", output)
            self.assertIn("Rate: 100.00, Amount: 50", output)
            self.assertIn("Rate: 103.00, Amount: 25", output)
            self.assertIn("Rate: 105.00, Amount: 30", output)

    # This tests if the show_tier_III_prices method correctly displays all transactions in the ledger.
    def test_show_tier_III_prices(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            self.ledger.show_tier_III_prices()
            output = fake_out.getvalue().strip()
            self.assertIn("Tier-III Prices (Full transaction depth):", output)
            self.assertIn("Rate: 102.00, Amount: 20", output)
            self.assertIn("Rate: 100.00, Amount: 50", output)
            self.assertIn("Rate: 103.00, Amount: 25", output)
            self.assertIn("Rate: 105.00, Amount: 30", output)
   
    # This tests if the PPU (Price Per Unit) calculator correctly computes the average price.
    def test_ppu_calculator(self):
        ppu = self.ledger.ppu_calculator.fetch_ppu()
        expected_ppu = (100*50 + 105*30 + 102*20 + 103*25) / (50 + 30 + 20 + 25)
        self.assertAlmostEqual(ppu, expected_ppu, places=2)

class TestPPUCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = PPUCalculator()

    # This tests if the PPU calculator correctly updates and calculates the average price.
    def test_refresh_and_fetch(self):
        self.calculator.refresh(100, 50)
        self.calculator.refresh(105, 30)
        ppu = self.calculator.fetch_ppu()
        expected_ppu = (100*50 + 105*30) / (50 + 30)
        self.assertAlmostEqual(ppu, expected_ppu, places=2)

    # This tests if the PPU calculator returns None when no transactions have been added.
    def test_fetch_ppu_empty(self):
        self.assertIsNone(self.calculator.fetch_ppu())

class TestSimulateTransactions(unittest.TestCase):

    @patch('random.choice', side_effect=['cap', 'acquire'])
    @patch('random.uniform', return_value=100)
    @patch('random.randint', return_value=50)

    def test_simulate_transactions(self, mock_randint, mock_uniform, mock_choice):
        # This tests if the simulate_transactions function correctly generates and adds transactions to the ledger.
        ledger = TradeLedger()
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            simulate_transactions(ledger, num_transactions=1)
            output = fake_out.getvalue().strip()
            self.assertIn("Added transaction: ID 1, Type cap, Direction acquire, Rate 100.00, Amount 50", output)

if __name__ == '__main__':
    unittest.main(verbosity=2)