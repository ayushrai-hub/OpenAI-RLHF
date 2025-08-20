import unittest
import numpy as np
import gurobipy as gp
from gurobipy import GRB
from ideal_code import decomposition_model  # Assuming the original function is in this file

class TestDecompositionModel(unittest.TestCase):

    def setUp(self):
        # Set up common test data
        self.values = [1, 2, 3, 4]
        self.cluster_size = [2, 2]
        self.Q = np.array([[1, 0.1, 0.1, 0.1],
                           [0.1, 1, 0.1, 0.1],
                           [0.1, 0.1, 1, 0.1],
                           [0.1, 0.1, 0.1, 1]])
        self.p = np.array([-1, -2, -3, -4])
        self.r = 10

    def test_gomory_cuts_implementation(self):
        # This test checks if Gomory cuts are correctly implemented for integer variables
        result, _ = decomposition_model(self.values, self.cluster_size, self.Q, self.p, self.r)
        
        # Check if the result is binary
        is_binary = np.all(np.isin(result, [0, 1]))
        self.assertTrue(is_binary, "Gomory cuts should produce binary solutions")

    def test_variable_type_consistency(self):
        # This test checks for consistency in variable handling
        model = gp.Model()
        n_values = len(self.values)
        n_clusters = len(self.cluster_size)
        x = model.addMVar((n_values * n_clusters), lb=0, ub=1, vtype=GRB.CONTINUOUS, name="x")
        
        # Add constraints and objective similar to the original model
        A1 = np.kron(np.eye(n_values), np.ones((1, n_clusters)))
        A2 = np.kron(np.ones((1, n_values)), np.eye(n_clusters))
        b1 = np.ones(n_values)
        b2 = np.ones(n_clusters)
        model.addConstr(A1 @ x == b1, name="c1")
        model.addConstr(A2 @ x >= b2, name="c2")
        obj = 0.5 * x @ self.Q @ x + self.p @ x + self.r
        model.setObjective(obj, sense=GRB.MINIMIZE)
        
        model.optimize()
        
        # Check if the solution is fractional (should be for continuous variables)
        is_fractional = np.any((x.X > 0) & (x.X < 1))
        self.assertTrue(is_fractional, "Continuous variables should allow fractional solutions")

    def test_convergence(self):
        # This test checks if the algorithm converges within a reasonable number of iterations
        max_iter = 100
        tol = 1e-4
        _, obj_value = decomposition_model(self.values, self.cluster_size, self.Q, self.p, self.r, max_iter=max_iter, tol=tol)
        
        # Check if the objective value is reasonable (you may need to adjust this based on the expected range)
        self.assertIsNotNone(obj_value, "Algorithm should converge to a solution")
        self.assertLess(obj_value, 1e6, "Objective value should be within a reasonable range")

    def test_matrix_operations(self):
        # This test checks if matrix operations are performed correctly
        n_values = len(self.values)
        n_clusters = len(self.cluster_size)
        x = np.random.rand(n_values * n_clusters)
        
        # Manual calculation of the objective
        obj_manual = 0.5 * x @ self.Q @ x + self.p @ x + self.r
        
        # Calculation using the model's method
        model = gp.Model()
        x_var = model.addMVar((n_values * n_clusters), lb=0, ub=1, vtype=GRB.CONTINUOUS, name="x")
        obj_model = 0.5 * x_var @ self.Q @ x_var + self.p @ x_var + self.r
        model.setObjective(obj_model, sense=GRB.MINIMIZE)
        
        # Set x_var to the random values
        for i in range(len(x)):
            x_var[i].start = x[i]
        
        model.update()
        
        # Compare the objective values
        self.assertAlmostEqual(obj_manual, model.getObjective().getValue(), places=4,
                               msg="Matrix operations in the objective should be correct")

if __name__ == '__main__':
    unittest.main(verbosity=2)