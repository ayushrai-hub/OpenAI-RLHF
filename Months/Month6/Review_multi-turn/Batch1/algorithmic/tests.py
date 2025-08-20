import unittest
import numpy as np
from ideal_completion import calculate_optimal_prices, plot_optimal_prices

class TestOptimalPriceCalculation(unittest.TestCase):
    def test_optimal_prices_range(self):
        """
        Tests that the function correctly computes optimal prices for a range of 's' values.
        This ensures the function's core logic accurately handles input variation over a
        continuous range and the output has the correct length, supporting functional integrity.
        """
        s_min, s_max, num_s = -15, 15, 30
        c, sigma_e = 0.1, 1
        s_values, p_optimal = calculate_optimal_prices(s_min, s_max, num_s, c, sigma_e)

        # Check if the length of the output matches the input specification
        self.assertEqual(len(s_values), num_s)
        self.assertEqual(len(p_optimal), num_s)

        # Check for increasing trend as a simple sanity check
        self.assertTrue(all(p_optimal[i] <= p_optimal[i + 1] for i in range(len(p_optimal) - 1)))

    def test_boundary_conditions(self):
        """
        Tests how the function handles near-boundary conditions for 's' values.
        This is important to confirm that the function robustly handles small ranges and
        still produces non-negative pricing, adhering to economic logic.
        """
        s_min, s_max, num_s = -1, 1, 10
        c, sigma_e = 0.1, 1
        s_values, p_optimal = calculate_optimal_prices(s_min, s_max, num_s, c, sigma_e)

        # Check if prices are never negative
        self.assertTrue(all(p >= 0 for p in p_optimal))

    def test_output_types(self):
        """
        Verifies that the output types of the function are numpy arrays.
        This is crucial for ensuring the function's outputs are consistent and compatible
        with expected data types for subsequent numerical or graphical analysis.
        """
        s_min, s_max, num_s = -15, 15, 30
        c, sigma_e = 0.1, 1
        s_values, p_optimal = calculate_optimal_prices(s_min, s_max, num_s, c, sigma_e)

        self.assertIsInstance(s_values, np.ndarray)
        self.assertIsInstance(p_optimal, np.ndarray)
    
    def test_plot_function(self):
        """
        Ensures the plotting function executes without raising errors.
        This test is crucial for verifying the plot function's robustness in handling valid inputs,
        contributing to reliable visualization capabilities.
        """
        try:
            s_min, s_max, num_s = -15, 15, 30
            c, sigma_e = 0.1, 1
            s_values, p_optimal = calculate_optimal_prices(s_min, s_max, num_s, c, sigma_e)
            plot_optimal_prices(s_values, p_optimal)
        except Exception as e:
            self.fail(f"Plotting function raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()