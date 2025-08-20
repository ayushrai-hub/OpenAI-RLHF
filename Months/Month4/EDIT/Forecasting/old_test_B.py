
import unittest
from datetime import datetime
from ideal_completion import plan_scenario

class TestPlanScenario(unittest.TestCase):

    def setUp(self):
        # Set up common mock inputs for different test cases
        self.mock_inputs = {
            'age_ratio': '0.8',
            'ratio': '1.2',
            'calc_date': datetime(2020, 1, 1),
            'birthdate': datetime(1960, 1, 1),
            'benefit year': 0,
            'urm status': 'active',
            'start_savings': 100000,
            'start_honorary_savings': 50000,
            'pensionbase': 30000,
            'year fraction retirement year': 0.75,
            'default retirement year': datetime(2080, 1, 1)  # Set retirement year far in the future
        }
        self.first_calc_year = 2020
        self.last_forecast_year = 2090  
        self.retire_year = 2080
        self.calc_year = 2020  # Assuming calc_year is the same as first_calc_year
        # Initial mock data for ALM and macro inputs
        self.mock_alm_inputs = [
            {'year': 2025, 'cohort': 65, 'scenario': 'baseline', 'op_cwf': 0.5, 'pp_cwf': 0.7,
             'total_return': 0.05, 'total_return_honorary': 0.04},
            {'year': 2026, 'cohort': 66, 'scenario': 'baseline', 'op_cwf': 0.6, 'pp_cwf': 0.8,
             'total_return': 0.06, 'total_return_honorary': 0.05},
        ]
        
        self.mock_macro_inputs = [
            {'year': 2025, 'sr_change': 0.01, 'scenario': 'baseline', 'payout_change': 0.02,
             'annual_inflation': 0.03, 'ff': 1.05, 'cpi': 1.02, 'contribution_rate': 0.05},
            {'year': 2026, 'sr_change': 0.02, 'scenario': 'baseline', 'payout_change': 0.03,
             'annual_inflation': 0.04, 'ff': 1.06, 'cpi': 1.03, 'contribution_rate': 0.06},
        ]

    def test_basic_scenario(self):
        """Test a basic pre-retirement scenario."""
        result = plan_scenario(2020, 2030, 'baseline', self.mock_inputs,
                               self.mock_alm_inputs, self.mock_macro_inputs,
                               65, 2025, 2020, 2020, 2020)
        self.assertIsNotNone(result)
        self.assertEqual(result['scenario_type'], 'baseline')
        self.assertEqual(result['status'], 'active')

    def test_already_retired(self):
        """Test the case where the user is already retired."""
        self.mock_inputs['urm status'] = 'retired'
        # Make sure mock_macro_inputs has non-zero values for cpi and annual_inflation
        self.mock_macro_inputs[0]['cpi'] = 1.02
        self.mock_macro_inputs[0]['annual_inflation'] = 0.03

        result = plan_scenario(2020, 2030, 'baseline', self.mock_inputs,
                               self.mock_alm_inputs, self.mock_macro_inputs,
                               65, 2019, 2020, 2020, 2020)
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'retired')

    def test_edge_case_age_and_year(self):
        """Test edge case where retire year and forecast year are very close."""
        result = plan_scenario(2020, 2025, 'baseline', self.mock_inputs,
                               self.mock_alm_inputs, self.mock_macro_inputs,
                               65, 2025, 2020, 2020, 2020)
        self.assertIsNotNone(result)
        self.assertLessEqual(result['years_to_build'], 6)

    def test_zero_twod_initial_ff(self):
        """Test the case where 'ff' in twod_initial is zero, which could lead to division by zero."""
        self.mock_macro_inputs[0]['ff'] = 0  # Set finance factor to zero
        result = plan_scenario(2020, 2030, 'baseline', self.mock_inputs,
                               self.mock_alm_inputs, self.mock_macro_inputs,
                               65, 2025, 2020, 2020, 2020)
        self.assertIsNotNone(result)
        # Ensure the result does not crash on division by zero
        self.assertGreaterEqual(result['mutation_factor'], 0)

    def test_extreme_future_year(self):
        """Test a scenario where we forecast to a far future year."""
        # Update default retirement year to match retire_year
        self.mock_inputs['default retirement year'] = datetime(2080, 1, 1)
        # Update retire_year to 2080
        retire_year = 2080
        # Ensure mock data covers up to 2090
        self.extend_mock_data(years=range(2025, 2091))  # Extend mock data up to 2090
        result = plan_scenario(
            first_calc_year=2020,
            last_forecast_year=2090,
            scenario_type='baseline',
            inputs=self.mock_inputs,
            alm_inputs=self.mock_alm_inputs,
            macro_inputs=self.mock_macro_inputs,
            retire_age=65,
            forecast_year=2020,
            retire_year=retire_year,
            first_year=2020,
            calc_year=2020
        )
        self.assertIsNotNone(result)
        # The years_to_build should be around 61 years (2080 - 2020 + 1)
        self.assertEqual(result['years_to_build'], 61)  # Expecting 61 years to build

    def extend_mock_data(self, years):
        for year in years:
            cohort = 60 + (year - self.first_calc_year)
            self.mock_alm_inputs.append({
                'year': year,
                'cohort': cohort,
                'scenario': 'baseline',
                'op_cwf': 0.5 + 0.01 * (year - 2025),
                'pp_cwf': 0.7 + 0.01 * (year - 2025),
                'total_return': 0.05 + 0.001 * (year - 2025),
                'total_return_honorary': 0.04 + 0.001 * (year - 2025)
            })
            self.mock_macro_inputs.append({
                'year': year,
                'sr_change': 0.01 + 0.001 * (year - 2025),
                'scenario': 'baseline',
                'payout_change': 0.02 + 0.001 * (year - 2025),
                'annual_inflation': 0.03 + 0.001 * (year - 2025),
                'ff': 1.05 + 0.01 * (year - 2025),
                'cpi': 1.02 + 0.01 * (year - 2025),
                'contribution_rate': 0.05 + 0.001 * (year - 2025)
            })

    def test_division_by_zero_handling(self):
        """Test division by zero safeguard in the determine_nominal_benefit."""
        # Set up inputs that would result in division by zero
        self.mock_macro_inputs[0]['ff'] = 0
        self.mock_alm_inputs[0]['op_cwf'] = 0
        result = plan_scenario(2020, 2030, 'baseline', self.mock_inputs,
                               self.mock_alm_inputs, self.mock_macro_inputs,
                               65, 2025, 2020, 2020, 2020)
        self.assertIsNotNone(result)
        # Verify that mutation factor is still calculated safely
        self.assertGreaterEqual(result['mutation_factor'], 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)

