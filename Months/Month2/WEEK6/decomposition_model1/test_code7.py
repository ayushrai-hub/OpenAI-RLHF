import unittest
import numpy as np
from gurobipy import GRB
from code7 import decomposition_model  
class TestDecompositionModel(unittest.TestCase):

    def setUp(self):
        # Common setup for all tests
        self.values = [1, 2, 3, 4, 5]
        self.cluster_size = [2, 3]
        self.n_vars = len(self.values) * len(self.cluster_size)
        self.Q = np.random.rand(self.n_vars, self.n_vars)
        self.Q = (self.Q + self.Q.T) / 2  # Ensure Q is symmetric
        self.p = np.random.rand(self.n_vars)
        self.r = 1.0

    def test_solution_shape(self):
        solution, _ = decomposition_model(self.values, self.cluster_size, self.Q, self.p, self.r)
        self.assertEqual(len(solution), self.n_vars)

    def test_solution_binary(self):
        solution, _ = decomposition_model(self.values, self.cluster_size, self.Q, self.p, self.r)
        self.assertTrue(np.all(np.logical_or(np.isclose(solution, 0), np.isclose(solution, 1))))

    def test_one_cluster_per_value(self):
        solution, _ = decomposition_model(self.values, self.cluster_size, self.Q, self.p, self.r)
        A1 = np.kron(np.eye(len(self.values)), np.ones(len(self.cluster_size)))
        self.assertTrue(np.allclose(A1 @ solution, 1))

    def test_min_one_value_per_cluster(self):
        solution, _ = decomposition_model(self.values, self.cluster_size, self.Q, self.p, self.r)
        A2 = np.kron(np.ones(len(self.values)), np.eye(len(self.cluster_size)))
        self.assertTrue(np.all(A2 @ solution >= 1))

    def test_objective_value(self):
        solution, objective = decomposition_model(self.values, self.cluster_size, self.Q, self.p, self.r)
        calculated_obj = 0.5 * solution @ self.Q @ solution + self.p @ solution + self.r
        self.assertAlmostEqual(objective, calculated_obj, places=5)

    def test_infeasible_problem(self):
        # Create an infeasible problem by setting impossible cluster sizes
        impossible_cluster_size = [100, 200]  # More than the number of values
        with self.assertRaises(Exception):  # Should raise an exception for infeasible problem
            decomposition_model(self.values, impossible_cluster_size, self.Q, self.p, self.r)

if __name__ == '__main__':
    unittest.main(verbosity=2)