import unittest
from io import StringIO
import sys

def calculate_change(change: int) -> str:
    output = []
    dol_value = change // 100
    quarter_value = (change % 100) // 25
    dime_value = (change % 25) // 10
    nickel_value = (change % 10) // 5
    penny_value = change % 5

    if change <= 0:
        return "No change"
    else:
        if dol_value > 1:
            output.append(f'{dol_value} Dollars')
        elif dol_value == 1:
            output.append(f'{dol_value} Dollar')
        if quarter_value > 1:
            output.append(f'{quarter_value} Quarters')
        elif quarter_value == 1:
            output.append(f'{quarter_value} Quarter')
        if dime_value > 1:
            output.append(f'{dime_value} Dimes')
        elif dime_value == 1:
            output.append(f'{dime_value} Dime')
        if nickel_value > 1:
            output.append(f'{nickel_value} Nickels')
        elif nickel_value == 1:
            output.append(f'{nickel_value} Nickel')
        if penny_value > 1:
            output.append(f'{penny_value} Pennies')
        elif penny_value == 1:
            output.append(f'{penny_value} Penny')
        
        return '\n'.join(output)

class TestChangeCalculator(unittest.TestCase):

    def test_no_change(self):
        self.assertEqual(calculate_change(0), "No change")
        self.assertEqual(calculate_change(-5), "No change")

    def test_single_denomination(self):
        self.assertEqual(calculate_change(1), "1 Penny")
        self.assertEqual(calculate_change(5), "1 Nickel")
        self.assertEqual(calculate_change(10), "1 Dime")
        self.assertEqual(calculate_change(25), "1 Quarter")
        self.assertEqual(calculate_change(100), "1 Dollar")

    def test_multiple_denominations(self):
        self.assertEqual(calculate_change(67), "2 Quarters\n1 Dime\n1 Nickel\n2 Pennies")
        self.assertEqual(calculate_change(99), "3 Quarters\n2 Dimes\n4 Pennies")

    def test_large_amount(self):
        self.assertEqual(calculate_change(1234), "12 Dollars\n1 Quarter\n1 Nickel\n4 Pennies")

    def test_all_denominations(self):
        self.assertEqual(calculate_change(141), "1 Dollar\n1 Quarter\n1 Dime\n1 Nickel\n1 Penny")

if __name__ == '__main__':
    unittest.main(verbosity=2)