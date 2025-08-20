import unittest
from datetime import datetime, date
from ideal_completion import (
    find_retiring,
    is_retiring_start_year,
    start_plan_year,
)

class TestIdealCompletion(unittest.TestCase):
    def test_find_retiring(self):
        # Test when forecast date is before birthday in the year
        age = 65
        xi = 0.5
        retire_age = 66
        birthdate = date(1955, 6, 15)
        forecast_date = date(2021, 6, 14)
        result = find_retiring(age, xi, retire_age, birthdate, forecast_date)
        self.assertFalse(result)

        # Test when forecast date is on or after birthday
        forecast_date = date(2021, 6, 15)
        result = find_retiring(age, xi, retire_age, birthdate, forecast_date)
        self.assertTrue(result)

    def test_is_retiring_start_year(self):
        # Test when benefit year is zero and retirement year matches
        inputs = {
            'default retirement year': datetime(2025, 1, 1),
            'benefit year': 0.0
        }
        year = 2025
        result = is_retiring_start_year(inputs, year)
        self.assertTrue(result)

        # Test when year does not match retirement year
        year = 2024
        result = is_retiring_start_year(inputs, year)
        self.assertFalse(result)

    def test_start_plan_year(self):
        # Test with sample inputs and check output keys
        forecast_year = 1
        ratio = 0.6
        fraction_in_calc_year = 0.5
        xi = 0.5
        retire_year = 2025
        year = 2023
        age = 65
        inputs = {
            'start_savings': 100000.0,
            'calc_date': datetime(2023, 1, 1),
            'birthdate': datetime(1958, 1, 1),
            'start_honorary_savings': 50000.0,
            'benefit year': 0.0,
            'default retirement year': datetime(retire_year, 1, 1),
            'urm status': 'active'
        }
        twod_initial = {
            'sr_change': 0.01,
            'annual_inflation': 0.02,
            'cpi': 1.0,
            'payout_change': 0.03
        }
        twod_next = twod_initial
        fourd_initial_age_init = {
            'op_cwf': 0.05,
            'pp_cwf': 0.02,
            'total_return': 0.07,
            'total_return_honorary': 0.06
        }
        fourd_initial_age_next = fourd_initial_age_init
        fourd_next_age_next = fourd_initial_age_init
        fourd_next_age_after = fourd_initial_age_init

        result = start_plan_year(
            forecast_year,
            ratio,
            fraction_in_calc_year,
            xi,
            retire_year,
            year,
            age,
            inputs,
            twod_initial,
            twod_next,
            fourd_initial_age_init,
            fourd_initial_age_next,
            fourd_next_age_next,
            fourd_next_age_after,
            retire_age=67
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result['year'], year)
        self.assertIn('nominal_benefit', result)
        self.assertIn('real_benefit', result)
        self.assertIn('savings_ordinary', result)

if __name__ == "__main__":
    unittest.main(verbosity=2)