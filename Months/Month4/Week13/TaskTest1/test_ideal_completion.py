import unittest
import numpy as np
from ideal_completion import (
    execute_DualTri, calculate_lipschitz, calculate_step_sizes,
    Compute_y, calculate_sum_u_neighbors, update_variables,
    check_convergence, grad_H
)

class TestDualTri(unittest.TestCase):

    def setUp(self):
        # Set up common test parameters
        self.Total_Nodes = 3
        self.Data_Size = 10
        self.Total_Equations_per_Node = 5
        self.y_opt_ini = np.random.rand(self.Data_Size)
        self.y_start = np.zeros(self.Data_Size)
        self.Total_Iter = 100
        self.nu = np.ones(self.Total_Nodes)
        self.nu_adjust = np.ones(self.Total_Nodes)
        self.gamma_rate = 0.1
        self.W_link_matrix = np.random.randint(0, 2, (self.Total_Nodes, self.Total_Nodes))
        np.fill_diagonal(self.W_link_matrix, 1)
        self.Q = [np.random.rand(self.Total_Equations_per_Node, self.Data_Size) for _ in range(self.Total_Nodes)]
        self.a = [np.random.rand(self.Total_Equations_per_Node) for _ in range(self.Total_Nodes)]
        self.Q_trial = np.random.rand(self.Total_Equations_per_Node, self.Data_Size)
        self.a_trial = np.random.rand(self.Total_Equations_per_Node)

    def test_execute_DualTri(self):
        # Test the main function to ensure it runs without errors and returns expected output shapes
        cost_function = 'L2'
        requires_central_solution = True
        return_y = False

        y_error_duration, y_avgconsensus_duration, y_opt_summary, y_opt = execute_DualTri(
            self.y_opt_ini, self.y_start, self.Total_Iter, cost_function, self.Total_Nodes, self.Data_Size,
            self.nu, self.nu_adjust, self.gamma_rate, self.W_link_matrix, requires_central_solution, 
            return_y, self.Q, self.a, self.Q_trial, self.a_trial
        )

        # Check output shapes
        self.assertEqual(y_error_duration.shape, (self.Total_Nodes, self.Total_Iter))
        self.assertEqual(y_avgconsensus_duration.shape, (self.Total_Nodes, self.Total_Iter))
        self.assertEqual(y_opt_summary.shape, (self.Data_Size,))
        self.assertEqual(y_opt.shape, (self.Data_Size,))

    def test_calculate_lipschitz(self):
        # Test Lipschitz constant calculation for different cost functions
        Q_norm = np.linalg.norm(self.Q[0].T @ self.Q[0])
        
        # Test L2 cost function
        L2_lipschitz = calculate_lipschitz('L2', self.nu[0], self.nu_adjust[0], Q_norm)
        self.assertGreater(L2_lipschitz, 0)  # Lipschitz constant should be positive

        # Test Huber cost function
        Huber_lipschitz = calculate_lipschitz('Huber', self.nu[0], self.nu_adjust[0], Q_norm)
        self.assertGreater(Huber_lipschitz, 0)

    def test_calculate_step_sizes(self):
        # Test step size calculation
        beta, alpha = calculate_step_sizes(self.Q, self.nu, self.nu_adjust, self.W_link_matrix, 'L2')

        # Check if step sizes are positive and within expected ranges
        self.assertTrue(all(b > 0 for b in beta))
        self.assertTrue(all(b < 1 for b in beta))
        self.assertTrue(all(a > 0 for a in alpha))
        self.assertTrue(all(a < 1 for a in alpha))

    def test_Compute_y(self):
        # Test global optimization function
        cost_function = 'L2'
        max_nu = max(self.nu)
        max_nu_adjust = max(self.nu_adjust)

        y_opt = Compute_y(self.y_opt_ini, self.Q, self.a, max_nu, max_nu_adjust, self.gamma_rate, cost_function)

        # Check if the output has the correct shape and is different from the initial guess
        self.assertEqual(y_opt.shape, self.y_opt_ini.shape)
        self.assertFalse(np.allclose(y_opt, self.y_opt_ini))

    def test_calculate_sum_u_neighbors(self):
        # Test calculation of sum of neighbor contributions
        v = 0
        y_k = [np.random.rand(self.Data_Size) for _ in range(self.Total_Nodes)]
        u_k = [[np.zeros(self.Data_Size) if self.W_link_matrix[m, k] == 1 else 0 
                for m in range(self.Total_Nodes)] for k in range(self.Total_Nodes)]
        theta = np.logical_or(self.W_link_matrix, np.eye(self.Total_Nodes)).astype(int)
        Data_Size_values = np.ones(self.Total_Nodes, dtype=int) * self.Data_Size

        sum_u = calculate_sum_u_neighbors(v, self.Total_Nodes, self.W_link_matrix, u_k, y_k, 
                                        theta, Data_Size_values, 'L2', self.a)

        # Check if the output has the correct shape
        self.assertEqual(sum_u.shape, (self.Data_Size,))

    def test_update_variables(self):
        # Test variable update for different cost functions
        v = 0
        z = np.random.rand(self.Total_Equations_per_Node)
        beta = 0.1
        Q = self.Q[v]
        y_k = np.random.rand(self.Data_Size)
        alpha = 0.1
        sum_u_neighbors = np.zeros(self.Data_Size)

        for cost_function in ['L2', 'Huber', 'MC', 'L1']:
            z_new, y_k1 = update_variables(v, z, beta, Q, y_k, alpha, sum_u_neighbors,
                                         self.nu[v], self.nu_adjust[v], self.gamma_rate, 
                                         cost_function, self.a[v])

            # Check if the outputs have the correct shapes
            self.assertEqual(z_new.shape, z.shape)
            self.assertEqual(y_k1.shape, y_k.shape)

    def test_check_convergence(self):
        # Test convergence check
        y_k = [np.random.rand(self.Data_Size) * 1e-7 for _ in range(self.Total_Nodes)]
        
        # Should converge
        self.assertTrue(check_convergence(y_k, 'L2', 20))
        
        # Should not converge (m < 10)
        self.assertFalse(check_convergence(y_k, 'L2', 5))
        
        # Should not converge (y_gap too large)
        y_k_large = [np.random.rand(self.Data_Size) * 1e-3 for _ in range(self.Total_Nodes)]
        self.assertFalse(check_convergence(y_k_large, 'L2', 20))

    def test_grad_H(self):
        # Test gradient calculation for different cost functions
        y = np.random.rand(self.Data_Size)
        Q = self.Q[0]
        a = self.a[0]

        for cost_function in ['MC', 'L1', 'L2', 'Huber', 'Tukey', 'Exponential', 'Hyperbolic', 'FairPotential']:
            grad = grad_H(y, self.nu[0], self.nu_adjust[0], self.gamma_rate, cost_function, Q, a)
            self.assertEqual(grad.shape, y.shape)

if __name__ == '__main__':
    unittest.main(verbosity=2)