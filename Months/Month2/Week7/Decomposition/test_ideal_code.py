import unittest
import numpy as np
import time  # Add this import
from testable_ideal_code import decomposition_model

class TestDecompositionModel(unittest.TestCase):
    def setUp(self):
        # Set up common test data
        self.values = [1, 2, 3, 4]
        self.cluster_size = [2, 2]
        self.n_vars = len(self.values) * len(self.cluster_size)
        self.Q = np.random.rand(self.n_vars, self.n_vars)
        self.Q = 0.5 * (self.Q + self.Q.T)  # Make Q symmetric
        self.p = np.random.rand(self.n_vars)
        self.r = 1.0

    def test_output_shape(self):
        x_opt, f_opt = decomposition_model(self.values, self.cluster_size, self.Q, self.p, self.r)
        self.assertIsNotNone(x_opt)
        self.assertIsNotNone(f_opt)
        self.assertEqual(len(x_opt), self.n_vars)

    def test_binary_solution(self):
        x_opt, _ = decomposition_model(self.values, self.cluster_size, self.Q, self.p, self.r)
        self.assertTrue(np.all(np.logical_or(np.isclose(x_opt, 0), np.isclose(x_opt, 1))))

    def test_constraint_satisfaction(self):
        x_opt, _ = decomposition_model(self.values, self.cluster_size, self.Q, self.p, self.r)
        A1 = np.kron(np.eye(len(self.values)), np.ones(len(self.cluster_size)))
        A2 = np.kron(np.ones(len(self.values)), np.eye(len(self.cluster_size)))
        
        self.assertTrue(np.allclose(A1 @ x_opt, 1))
        self.assertTrue(np.all(A2 @ x_opt >= 1))

    def test_objective_value(self):
        x_opt, f_opt = decomposition_model(self.values, self.cluster_size, self.Q, self.p, self.r)
        calculated_obj = 0.5 * x_opt @ self.Q @ x_opt + self.p @ x_opt + self.r
        self.assertAlmostEqual(f_opt, calculated_obj, places=4)

    def test_infeasible_problem(self):
        # Create an infeasible problem by setting conflicting constraints
        infeasible_values = [1]
        infeasible_cluster_size = [2, 2]  # Sum is greater than number of values
        x_opt, f_opt = decomposition_model(infeasible_values, infeasible_cluster_size, self.Q, self.p, self.r)
        self.assertIsNone(x_opt)
        self.assertIsNone(f_opt)

    def test_convergence(self):
        # Test with very small problem to ensure quick convergence
        small_values = [1, 2]
        small_cluster_size = [1, 1]
        small_n_vars = len(small_values) * len(small_cluster_size)
        small_Q = np.random.rand(small_n_vars, small_n_vars)
        small_Q = 0.5 * (small_Q + small_Q.T)
        small_p = np.random.rand(small_n_vars)
        
        start_time = time.time()
        x_opt, f_opt = decomposition_model(small_values, small_cluster_size, small_Q, small_p, self.r)
        end_time = time.time()
        
        self.assertIsNotNone(x_opt)
        self.assertIsNotNone(f_opt)
        self.assertLess(end_time - start_time, 5)  # Should converge in less than 5 seconds

if __name__ == '__main__':
    unittest.main(verbosity=2)