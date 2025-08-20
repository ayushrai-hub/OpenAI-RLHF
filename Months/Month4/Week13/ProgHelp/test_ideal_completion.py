import unittest
import numpy as np
from numpy.testing import assert_array_almost_equal
from testable_ideal_solution import gelu, improved_step_transition
class TestGELUStepTransition(unittest.TestCase):
    def setUp(self):
        # It sets up test cases with common input values and parameters
        # It creates arrays of test values that will be reused across multiple tests:
        self.x_values = np.linspace(-4, 4, 1000)
        self.test_points = np.array([-2, -0.5, 0, 0.5, 2])
        self.beta_values = np.array([1.0, 0.5, 0.1, 0.01])
        
    def test_gelu_properties(self):
        # It tests basic properties of GELU function
        # Test GELU at zero, which is the fundamental property of the function
        self.assertAlmostEqual(gelu(0), 0, places=6)
        
        # Test GELU monotonicity for positive values
        x_positive = np.linspace(0, 4, 100)
        gelu_vals = gelu(x_positive)
        differences = np.diff(gelu_vals)
        self.assertTrue(np.all(differences >= 0))

    def test_improved_step_transition_bounds(self):
        # It tests if the transition function stays within expected bounds
        # These properties aer crucial for maintaing stable behavior when used in larger systems or neural networks.
        for beta in self.beta_values:
            output = improved_step_transition(self.x_values, beta)
            # Test output is bounded between 0 and 1
            self.assertTrue(np.all(output >= 0))
            self.assertTrue(np.all(output <= 1))
            
            # Test specific points
            zero_output = improved_step_transition(0, beta)
            self.assertGreaterEqual(zero_output, 0)
            self.assertLessEqual(zero_output, 1)

    def test_beta_parameter_behavior(self):
        # It tests behavior of the function:
        # It test very small beta (step-like behavior)
        small_beta = 0.01
        test_x = np.array([-1.0, 1.0])
        step_output = improved_step_transition(test_x, small_beta)
        expected_step = np.array([0.0, 1.0])
        assert_array_almost_equal(step_output, expected_step, decimal=1)

    def test_continuity(self):
        # It tests if the function is continous (no sudden jumps)
        # Test with extra fine-grained x values around critical points
        # Continuity is essential for gradient-based optimization and preventing numerical instabilities in applications
        x_critical = np.linspace(-0.5, 0.5, 1000)
        for beta in self.beta_values:
            output = improved_step_transition(x_critical, beta)
            differences = np.abs(np.diff(output))
            max_diff = np.max(differences)
            # For small beta, allow slightly larger differences
            max_allowed = 0.1 if beta >= 0.1 else 0.2
            self.assertTrue(max_diff < max_allowed, 
                          f"Discontinuity detected: {max_diff} with beta={beta}")

    def test_numerical_stability(self):
        # It tests numerical stability with extreme inputs
        # It is essential for real-world applications where inputs might not be well-bounded or normalized.
        extreme_x = np.array([-1e3, -1e2, -10, -1, 0, 1, 10, 1e2, 1e3])
        for beta in self.beta_values:
            output = improved_step_transition(extreme_x, beta)
            self.assertTrue(np.all(np.isfinite(output)))
            self.assertTrue(np.all(output >= 0))
            self.assertTrue(np.all(output <= 1))

    def test_zero_crossing(self):
        # It tests behavior around zero.
        # Zero-crossing behvior is particularly important as it's often a critical point in applications and should maintain smooth, well-defined behsvior.
        x_near_zero = np.linspace(-0.1, 0.1, 200)
        for beta in self.beta_values:
            output = improved_step_transition(x_near_zero, beta)
            # Test smoothness around zero
            differences = np.diff(output)
            self.assertTrue(np.all(np.abs(differences) < 0.1))
            # Test symmetry around zero for large beta
            if beta > 0.5:
                mid_point = len(x_near_zero) // 2
                self.assertAlmostEqual(output[mid_point], 0.5, places=2)

if __name__ == '__main__':
    unittest.main(verbosity=2)