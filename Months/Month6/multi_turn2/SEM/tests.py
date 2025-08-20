import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np
import warnings
from ideal_completion import estimate_keyword_strengths

# Sample synthetic data based on provided pattern with additional metrics
def get_sample_data():
    return pd.DataFrame({
        'keyword': ['kw1', 'kw2', 'kw3', 'kw4', 'kw5', 'kw1', 'kw2', 'kw3', 'kw4', 'kw5',
                    'kw1', 'kw2', 'kw3', 'kw4', 'kw5', 'kw1', 'kw2', 'kw3', 'kw4', 'kw5'],
        'week': [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4],
        'clicks': [100, 80, 60, 90, 110, 105, 85, 70, 95, 115, 120, 95, 75, 100, 130, 110, 100, 90, 120, 125],
        'gp': [600, 400, 360, 500, 660, 550, 450, 400, 570, 690, 700, 480, 375, 620, 780, 690, 600, 540, 720, 800],
        'impressions': [1000, 900, 850, 870, 1200, 1100, 950, 930, 990, 1180, 1220, 980, 760, 1010, 1350, 1150, 1000, 890, 1250, 1300],
        'cost': [100, 80, 60, 90, 110, 105, 85, 70, 95, 115, 120, 95, 75, 100, 130, 110, 100, 90, 120, 125],
        'conversions': [5, 4, 3, 4, 6, 5, 4, 3, 4, 6, 7, 4, 3, 6, 8, 7, 6, 5, 7, 8],
    })

class TestBTLModel(unittest.TestCase):

    def setUp(self):
        # Load sample data
        self.data = get_sample_data()
        # Suppress specific warnings, such as RuntimeWarning
        warnings.filterwarnings("ignore", category=RuntimeWarning)

    @patch('builtins.print')  # Mock print to suppress output
    def test_gpc_calculation(self, mock_print):
        _, data_with_gpc, _, _ = estimate_keyword_strengths(self.data)
        self.assertTrue('gpc' in data_with_gpc.columns)
        for _, row in data_with_gpc.iterrows():
            self.assertAlmostEqual(row['gpc'], row['gp'] / row['clicks'] if row['clicks'] > 0 else 0)

    @patch('builtins.print')  # Mock print to suppress output
    def test_pairwise_comparisons(self, mock_print):
        _, _, pairwise_stats, _ = estimate_keyword_strengths(self.data)
        self.assertTrue(len(pairwise_stats) > 0)
        for (i, j), weight in pairwise_stats.items():
            self.assertGreater(weight, 0)

    @patch('builtins.print')  # Mock print to suppress output
    def test_theta_calculation(self, mock_print):
        theta_values, _, _, _ = estimate_keyword_strengths(self.data)
        self.assertEqual(len(theta_values), len(self.data['keyword'].unique()))
        for theta in theta_values.values():
            self.assertGreater(theta, 0)

    @patch('builtins.print')  # Mock print to suppress output
    def test_algorithm_convergence(self, mock_print):
        _, _, _, optimization_result = estimate_keyword_strengths(self.data)
        
        self.assertTrue(optimization_result.success, "The optimization did not converge successfully.")
        
        # Check if the gradient norm is small (indicating convergence)
        gradient_norm = np.linalg.norm(optimization_result.jac)
        self.assertLess(gradient_norm, 1e-5, "The gradient norm should be small if the optimization converged.")
        
        # Ensure that the final function value (NLL) is not inf or extremely high
        self.assertLess(optimization_result.fun, 1e6, "The final NLL should be reasonably low, indicating convergence.")

if __name__ == '__main__':
    unittest.main(verbosity=2)