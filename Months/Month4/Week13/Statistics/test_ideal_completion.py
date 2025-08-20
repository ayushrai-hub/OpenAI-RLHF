import numpy as np
import unittest
from numpy.testing import assert_almost_equal
from testable_ideal_completion import one_var_lasso 

class TestOneVarLasso(unittest.TestCase):
    def setUp(self):
        # It sets up test cases with different scenarios for thorough testing.
        # Test case 1: Simple case where we expect non-zero coefficient expected.
        self.v1 = np.array([2.3, 4.5, 1.2, 3.8, 2.2])
        self.z1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        self.lambda1 = 0.5
        
        # Test case 2: Special case where we expect zero coefficient
        self.v2 = np.array([1.0, -1.0, 1.0, -1.0])
        self.z2 = np.array([1.0, 1.0, 1.0, 1.0])
        self.lambda2 = 10.0
        
        # Test case 3: Edge case with minimal data
        self.v3 = np.array([2.0])
        self.z3 = np.array([1.0])
        self.lambda3 = 0.1

    def test_input_validation(self):
        # Test that function handles invalid inputs appropriately.
        # The empty arrays should raise error.
        with self.assertRaises(ValueError):
            one_var_lasso(np.array([]), np.array([]), 0.5)
            
        # Different length vectors would give invalid results.
        with self.assertRaises(ValueError):
            one_var_lasso(self.v1, self.z1[:3], 0.5)
            
        # Test negative lambda
        with self.assertRaises(ValueError):
            one_var_lasso(self.v1, self.z1, -0.5)
            
        # Test zero vector
        with self.assertRaises(ValueError):
            one_var_lasso(self.v1, np.zeros_like(self.z1), 0.5)

    def test_ols_solution(self):
        # Test that lambda=0 gives Ordinary Least Squares solution.
        result = one_var_lasso(self.v1, self.z1, 0.0)
        ols_solution = np.dot(self.v1, self.z1) / np.dot(self.z1, self.z1)
        assert_almost_equal(result, ols_solution, decimal=5)

    def test_zero_solution(self):
        # It tests that sufficiently large lambda gives zero coefficient to zero.
        result = one_var_lasso(self.v2, self.z2, self.lambda2)
        assert_almost_equal(result, 0.0, decimal=5)

    def test_single_element(self):
        # It tests edge case with single-element vectors.
        result = one_var_lasso(self.v3, self.z3, self.lambda3)
        expected = max(0, abs(self.v3[0]) - self.lambda3) * np.sign(self.v3[0])
        assert_almost_equal(result, expected, decimal=5)

    def test_kkt_conditions(self):
        # It tests that solution satisfies KKT conditions
        result = one_var_lasso(self.v1, self.z1, self.lambda1)
        n = len(self.v1)
        vt_z = np.dot(self.v1, self.z1)
        z_norm_sq = np.dot(self.z1, self.z1)
        
        if result != 0:
            # For non-zero solution, check gradient condition
            gradient = -vt_z + result * z_norm_sq + n * self.lambda1 * np.sign(result)
            assert_almost_equal(gradient, 0, decimal=5)
        else:
            # For zero solution, check subgradient condition
            self.assertTrue(abs(vt_z) <= n * self.lambda1)

    def test_symmetry(self):
        # It tests that the function exhibits expected symmetry"""
        result1 = one_var_lasso(self.v1, self.z1, self.lambda1)
        result2 = one_var_lasso(-self.v1, self.z1, self.lambda1)
        assert_almost_equal(result1, -result2, decimal=5)

if __name__ == '__main__':
    unittest.main(verbosity=2)