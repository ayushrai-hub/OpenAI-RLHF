import unittest
from datetime import date
from decimal import Decimal
from testable_ideal_completion import get_month_start, parse_date, process_liabilities

class TestLiabilityCalculations(unittest.TestCase):

    def setUp(self):
        # Set up sample liability data for use in multiple tests
        self.sample_liabilities = [
            {"type": "Car Loan", "start_date": "2023-01-01", "end_date": "2023-12-31", "balance": 1000},
            {"type": "Store Card", "start_date": "2023-03-01", "end_date": "2023-09-30", "balance": 500},
            {"type": "Home Loan", "start_date": "2023-04-01", "end_date": "2023-06-30", "balance": 800},
            {"type": "Store Card", "start_date": "2023-04-01", "end_date": "2023-07-30", "balance": 2000},
            {"type": "Store Card", "start_date": "2023-04-01", "end_date": "2023-09-30", "balance": 2000}
        ]

    def test_get_month_start(self):
        # Test the get_month_start function to ensure it correctly calculates the start of a month
        reference_date = date(2023, 12, 31)
        self.assertEqual(get_month_start(reference_date, 1), date(2023, 11, 1))
        self.assertEqual(get_month_start(reference_date, 12), date(2022, 12, 1))

    def test_parse_date(self):
        # Test the parse_date function to ensure it correctly converts string dates to date objects
        self.assertEqual(parse_date("2023-01-01"), date(2023, 1, 1))
        # Also test that it raises a ValueError for incorrect date formats
        with self.assertRaises(ValueError):
            parse_date("2023/01/01")

    def test_empty_liabilities(self):
        # This ensures the function handles edge cases correctly and doesn't break with no input
        time_windows = [1, 3, 6]
        results = process_liabilities([], time_windows)
        self.assertEqual(results, [])

    def test_invalid_date_format(self):
        # This ensures the function properly validates input data and raises appropriate errors
        invalid_liabilities = [
            {"type": "Invalid Loan", "start_date": "2023/01/01", "end_date": "2023-12-31", "balance": 1000}
        ]
        with self.assertRaises(ValueError):
            process_liabilities(invalid_liabilities, [1])

    def test_missing_key(self):
        # This ensures the function properly checks for all required fields in liability data
        invalid_liabilities = [
            {"type": "Invalid Loan", "start_date": "2023-01-01", "balance": 1000}  # Missing end_date
        ]
        with self.assertRaises(ValueError):
            process_liabilities(invalid_liabilities, [1])

    def test_negative_balance(self):
        # This ensures the function correctly handles negative values, which might represent credits or overpayments
        negative_balance_liabilities = [
            {"type": "Negative Loan", "start_date": "2023-01-01", "end_date": "2023-12-31", "balance": -1000}
        ]
        results = process_liabilities(negative_balance_liabilities, [1])
        self.assertLess(results[0][3], 0)  # Check if total balance is negative

if __name__ == '__main__':
    unittest.main(verbosity=2)