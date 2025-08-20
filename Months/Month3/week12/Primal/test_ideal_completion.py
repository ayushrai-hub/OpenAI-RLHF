import unittest
import numpy as np
from scipy.linalg import norm
from testable_ideal_solution import execute_DualTri, calculate_step_sizes, calculate_lipschitz, Compute_y, calculate_sum_u_neighbors, update_variables, update_u_k, calculate_metrics, check_convergence, grad_H

class TestDualTri(unittest.TestCase):
    # set up test data and parameters
    def setUp(self):
        self.Total_Nodes = 3
        self.Data_Size = 5
        self.Total_Iter = 100
        self.y_opt_ini = np.random.rand(self.Data_Size)
        self.y_start = np.random.rand(self.Data_Size)
        self.nu = np.random.rand(self.Total_Nodes)
        self.nu_adjust = np.random.rand(self.Total_Nodes)
        self.gamma_rate = 0.1
        self.W_link_matrix = np.random.randint(0, 2, (self.Total_Nodes, self.Total_Nodes))
        np.fill_diagonal(self.W_link_matrix, 0)
        self.Q = [np.random.rand(self.Data_Size, self.Data_Size) for _ in range(self.Total_Nodes)]
        self.a = [np.random.rand(self.Data_Size) for _ in range(self.Total_Nodes)]
        self.Q_trial = np.random.rand(self.Data_Size, self.Data_Size)
        self.a_trial = np.random.rand(self.Data_Size)

    def test_execute_DualTri(self):
        # This tests the main DualTri algorithm execution 
        cost_functions = ['MC', 'L1', 'L2', 'Huber', 'Tukey', 'Exponential', 'Hyperbolic', 'FairPotential']
        
        for cost_function in cost_functions:
            y_error_duration, y_avgconsensus_duration, y_opt_summary, y_opt = execute_DualTri(
                self.y_opt_ini, self.y_start, self.Total_Iter, cost_function, self.Total_Nodes,
                self.Data_Size, self.nu, self.nu_adjust, self.gamma_rate, self.W_link_matrix,
                True, True, self.Q, self.a, self.Q_trial, self.a_trial
            )
            
            self.assertEqual(y_error_duration.shape, (self.Total_Nodes, self.Total_Iter))
            self.assertEqual(y_avgconsensus_duration.shape, (self.Total_Nodes, self.Total_Iter))
            self.assertEqual(y_opt_summary.shape, (self.Data_Size,))
            self.assertEqual(y_opt.shape, (self.Data_Size,))

    def test_calculate_step_sizes(self):
        # This tests the calculation of step sizes
        beta, alpha = calculate_step_sizes(self.Q, self.nu, self.nu_adjust, self.W_link_matrix, 'L2')
        
        self.assertEqual(beta.shape, (self.Total_Nodes,))
        self.assertEqual(alpha.shape, (self.Total_Nodes,))
        self.assertTrue(np.all(beta > 0))
        self.assertTrue(np.all(alpha > 0))

    def test_calculate_lipschitz(self):
        # This tests the calculation of Lipschitz constants
        Q_norm = 1.0
        nu = 0.5
        nu_adjust = 0.3
        
        cost_functions = ['Exponential', 'FairPotential', 'Hyperbolic', 'MC_adjust', 'L1_adjust', 'MC', 'Huber']
        
        for cost_function in cost_functions:
            L = calculate_lipschitz(cost_function, nu, nu_adjust, Q_norm)
            self.assertGreater(L, 0)

    def test_Compute_y(self):
        # It tests the computation of y
        y_opt = Compute_y(self.y_opt_ini, self.Q, self.a, max(self.nu), max(self.nu_adjust),
                          self.gamma_rate, 'L2')
        
        self.assertEqual(y_opt.shape, (self.Data_Size,))

    def test_calculate_sum_u_neighbors(self):
        # This tests the calculation of the sum of neighboring u values
        u_k = [[np.zeros(self.Data_Size) for _ in range(self.Total_Nodes)] for _ in range(self.Total_Nodes)]
        y_k = [np.random.rand(self.Data_Size) for _ in range(self.Total_Nodes)]
        theta = np.logical_or(self.W_link_matrix, np.eye(self.Total_Nodes)).astype(int)
        Data_Size_values = np.full(self.Total_Nodes, self.Data_Size)
        
        sum_u = calculate_sum_u_neighbors(0, self.Total_Nodes, self.W_link_matrix, u_k, y_k,
                                          theta, Data_Size_values, 'L2', self.a)
        
        self.assertEqual(sum_u.shape, (self.Data_Size,))

    def test_update_variables(self):
        # This tests the update of variables z and y
        v = 0
        z = np.random.rand(self.Data_Size)
        beta = 0.1
        y_k = np.random.rand(self.Data_Size)
        alpha = 0.1
        sum_u_neighbors = np.zeros(self.Data_Size)
        
        cost_functions = ['MC', 'L1', 'L2', 'Huber', 'Tukey', 'Exponential', 'Hyperbolic', 'FairPotential']
        
        for cost_function in cost_functions:
            z_new, y_k1 = update_variables(v, z, beta, self.Q[v], y_k, alpha, sum_u_neighbors,
                                           self.nu[v], self.nu_adjust[v], self.gamma_rate,
                                           cost_function, self.a[v])
            
            self.assertEqual(z_new.shape, (self.Data_Size,))
            self.assertEqual(y_k1.shape, (self.Data_Size,))

    def test_update_u_k(self):
        # This tests the update of u_k
        u_k = [[np.zeros(self.Data_Size) for _ in range(self.Total_Nodes)] for _ in range(self.Total_Nodes)]
        y_k = [np.random.rand(self.Data_Size) for _ in range(self.Total_Nodes)]
        theta = np.logical_or(self.W_link_matrix, np.eye(self.Total_Nodes)).astype(int)
        Data_Size_values = np.full(self.Total_Nodes, self.Data_Size)
        
        update_u_k(0, self.Total_Nodes, self.W_link_matrix, u_k, theta, Data_Size_values,
                   'L2', self.a, y_k)
        
        self.assertEqual(len(u_k), self.Total_Nodes)
        self.assertTrue(all(len(u_k[i]) == self.Total_Nodes for i in range(self.Total_Nodes)))

    def test_calculate_metrics(self):
        # This test the calculation of metrics
        identity_zero_matr = [np.eye(self.Data_Size) for _ in range(self.Total_Nodes)]
        y_k = [np.random.rand(self.Data_Size) for _ in range(self.Total_Nodes)]
        y_opt_summary = np.random.rand(self.Data_Size)
        
        y_opt, y_error, y_avgconsensus = calculate_metrics(self.Total_Nodes, identity_zero_matr,
                                                           y_k, self.y_opt_ini, y_opt_summary,
                                                           True, self.Q_trial, self.a_trial)
        
        self.assertEqual(y_opt.shape, (self.Data_Size,))
        self.assertEqual(y_error.shape, (self.Total_Nodes,))
        self.assertEqual(y_avgconsensus.shape, (self.Total_Nodes,))

    def test_check_convergence(self):
        # This tests the convergence check
        y_k = [np.ones(5) for _ in range(3)]
        self.assertTrue(check_convergence(y_k, 'L2', 15))
        
        y_k[1] += 1e-7  # Smaller perturbation
        self.assertTrue(check_convergence(y_k, 'L2', 15))
        
        y_k[1] += 1e-5  # Larger perturbation
        self.assertFalse(check_convergence(y_k, 'L2', 15))

    def test_grad_H(self):
        # This test the gradient calculation
        y = np.random.rand(self.Data_Size)
        cost_functions = ['MC', 'L1', 'L2', 'Huber', 'Tukey', 'Exponential', 'Hyperbolic', 'FairPotential']
        
        for cost_function in cost_functions:
            grad = grad_H(y, self.nu[0], self.nu_adjust[0], self.gamma_rate, cost_function,
                          self.Q[0], self.a[0])
            
            self.assertEqual(grad.shape, (self.Data_Size,))

if __name__ == '__main__':
    unittest.main(verbosity=2)