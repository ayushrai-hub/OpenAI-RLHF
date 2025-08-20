import unittest
from testableIC import *
import numpy as np

class TestMonteCarloIMSEW(unittest.TestCase):

    def setUp(self):
        # Initial setup for each test method
        self.domain = [0, 1]
        self.num_samples = 1000
        results = [monte_carlo_imse_w(self.domain, self.num_samples) for _ in range(10)]  # Reduced iterations for simplicity
        self.mean_result = np.mean(results)
        self.std_dev = np.std(results)
        self.confidence_multiplier = 3  # 99.7% confidence interval
        self.lower_bound = self.mean_result - self.confidence_multiplier * self.std_dev
        self.upper_bound = self.mean_result + self.confidence_multiplier * self.std_dev

    def test_true_function(self):
        # Test the true function at specific points
        np.testing.assert_almost_equal(f(0), 0, decimal=5)
        np.testing.assert_almost_equal(f(0.25), 1, decimal=5)
        np.testing.assert_almost_equal(f(0.5), 0, decimal=5)
        np.testing.assert_almost_equal(f(0.75), -1, decimal=5)

    def test_surrogate_model_shape(self):
        # Test that the surrogate model outputs the correct shape
        x = np.array([0, 0.25, 0.5, 0.75])
        result = surrogate_model(x)
        self.assertEqual(result.shape, x.shape)

    def test_weight_function(self):
        # Test the weight function values
        self.assertAlmostEqual(w(0), 1, places=5)
        self.assertAlmostEqual(w(1), np.exp(-1), places=5)
        self.assertAlmostEqual(w(2), np.exp(-4), places=5)

    def test_monte_carlo_imse_w_within_range(self):
        # Test to check if the Monte Carlo simulation falls within the established range
        test_result = monte_carlo_imse_w(self.domain, self.num_samples)
        self.assertTrue(self.lower_bound <= test_result <= self.upper_bound)

if __name__ == '__main__':
    unittest.main(verbosity=2)