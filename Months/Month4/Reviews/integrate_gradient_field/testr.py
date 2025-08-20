import unittest
import numpy as np
from testable_IC import integrate_gradient_field
import matplotlib.pyplot as plt
from matplotlib.contour import QuadContourSet

class TestIntegrateGradientField(unittest.TestCase):

    def setUp(self):

        self.h = np.linspace(0, 10, 100)
        self.T = np.linspace(0, 100, 100)
        self.H, self.T_grid = np.meshgrid(self.h, self.T)
        self.dSdh = np.sin(self.H) * np.cos(self.T_grid)
        self.dSdT = np.cos(self.H) * np.sin(self.T_grid)
        self.boundary_value = 2

    def test_shape_of_S_grid(self):
        # Test that the output S grid has the same shape as input grids
        S, _, _ = integrate_gradient_field(self.dSdh.flatten(), self.dSdT.flatten(), self.H.flatten(), self.T_grid.flatten(), self.boundary_value)
        self.assertEqual(S.shape, self.H.shape)

    def test_boundary_value(self):
        # Test that boundary values at T=100 are set to the specified boundary_value
        S, _, T_grid = integrate_gradient_field(self.dSdh.flatten(), self.dSdT.flatten(), self.H.flatten(), self.T_grid.flatten(), self.boundary_value)
        boundary_indices = np.where(T_grid[:, 0] == 100)[0]
        for idx in boundary_indices:
            self.assertAlmostEqual(S[idx, 0], self.boundary_value)

    def test_plot_contour_graph(self):
        # Test that a QuadContourSet contour plot is generated
        S, H, T_grid = integrate_gradient_field(self.dSdh.flatten(), self.dSdT.flatten(), self.H.flatten(), self.T_grid.flatten(), self.boundary_value)
        with plt.ioff():
            fig, ax = plt.subplots()
            contour = ax.contourf(H, T_grid, S, levels=50, cmap='viridis')
            plt.close(fig)

        self.assertIsInstance(contour, QuadContourSet)

    def test_non_nan_values(self):
        # Test that the resulting S grid contains no NaN values
        S, _, _ = integrate_gradient_field(self.dSdh.flatten(), self.dSdT.flatten(), self.H.flatten(), self.T_grid.flatten(), self.boundary_value)
        self.assertFalse(np.isnan(S).any())

if __name__ == "__main__":
    unittest.main(verbosity=2)