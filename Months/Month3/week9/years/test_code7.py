import unittest
from testable_ideal_code import get_dates

class TestDatesList(unittest.TestCase):
    def setUp(self):
        self.dates = get_dates()  # Call main() to initialize the dates list
    # This test verifies the correct number of elements.
    def test_list_length(self):
        self.assertEqual(len(self.dates), 20, "The list should contain 20 elements")
    # This test ensures all elements are strings for consistency.
    def test_all_strings(self):
        self.assertTrue(all(isinstance(date, str) for date in self.dates), "All elements should be strings")
    # This test checks if the dates are in the correct order.
    def test_chronological_order(self):
        self.assertEqual(self.dates, sorted(self.dates), "Dates should be in chronological order")
    # This test ensure there are no repeated years.
    def test_no_duplicates(self):
        self.assertEqual(len(self.dates), len(set(self.dates)), "There should be no duplicate dates")

if __name__ == '__main__':
    unittest.main(verbosity=2)