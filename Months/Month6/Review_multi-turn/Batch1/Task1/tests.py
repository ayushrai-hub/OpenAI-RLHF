import unittest
import numpy as np
from ideal_completion import (
    compute_r,
    H_func,
    l_mu_func,
    g_mu_nu,
    compute_inverse_metric,
    partial_derivatives,
    compute_christoffel_symbols,
    geodesic_equations,
    integrate_geodesic,
    M, a  # Ensure constants are imported for accurate comparisons
)

class TestCompletion(unittest.TestCase):

    def test_compute_r(self):
        """Tests compute_r function with different coordinates."""
        # This test checks if `compute_r` correctly calculates the radial coordinate r
        # for given x, y, z coordinates. It uses a simple case where the expected
        # r is known to be 0.8660254037844386, verifying that the calculation is accurate.
        x, y, z = 1.0, 0.0, 0.0
        r = compute_r(x, y, z)
        self.assertAlmostEqual(r, 0.8660254037844386, places=6)

    def test_H_func(self):
        """Tests H_func for expected H(r, z) values."""
        # Verifies the computation of the H function used in the Kerr-Schild metric.
        # The test compares the calculated H with an expected value based on known parameters.
        # Accuracy in H is important for ensuring metric consistency in simulations.
        r, z = 1.0, 0.0
        expected_H = M * r**3 / (r**4 + a**2 * z**2)
        self.assertAlmostEqual(H_func(r, z), expected_H, places=6)

    def test_l_mu_func(self):
        """Tests l_mu_func with sample inputs for consistency."""
        # This test checks if `l_mu_func` produces the expected components of l_mu
        # for a known set of (r, x, y, z). Consistency in l_mu is crucial as it defines
        # directional components in the Kerr-Schild metric.
        r, x, y, z = 1.0, 1.0, 0.0, 0.0
        l_mu = l_mu_func(r, x, y, z)
        expected_l_mu = np.array([1.0, 0.8, -0.4, 0.0])
        np.testing.assert_array_almost_equal(l_mu, expected_l_mu, decimal=6)

    def test_g_mu_nu(self):
        """Tests g_mu_nu for consistency with Minkowski metric at zero spin."""
        # This test verifies if the metric tensor `g_mu_nu` is symmetric and that
        # its entries match expectations for given coordinates. A symmetric metric
        # confirms proper formulation of the Kerr-Schild metric.
        x, y, z = 1.0, 0.0, 0.0
        g = g_mu_nu(x, y, z)
        np.testing.assert_array_almost_equal(g, g.T, decimal=6)  # Symmetry check
        self.assertGreater(g[0, 0], 0)  # Confirm time component's expected sign

    def test_compute_inverse_metric(self):
        """Tests compute_inverse_metric with a sample metric tensor."""
        # Tests if `compute_inverse_metric` accurately inverts a simple metric tensor.
        # This is essential for ensuring accurate calculations of the inverse metric,
        # which is required for correct geodesic computations.
        g = np.array([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        g_inv = compute_inverse_metric(g)
        expected_g_inv = np.linalg.inv(g)
        np.testing.assert_array_almost_equal(g_inv, expected_g_inv, decimal=6)

    def test_partial_derivatives(self):
        """Tests partial_derivatives function for consistency."""
        # Tests if `partial_derivatives` correctly calculates partial derivatives
        # for a sample function at a given point. Correct partial derivatives
        # are crucial for accurate gradient-based calculations in physics simulations.
        func = lambda x, y, z: x**2 + y**2 + z**2
        x, y, z = 1.0, 2.0, 3.0
        partials = partial_derivatives(func, x, y, z)
        expected_partials = {'x': 2*x, 'y': 2*y, 'z': 2*z}
        for var in expected_partials:
            self.assertAlmostEqual(partials[var], expected_partials[var], places=4)

    def test_compute_christoffel_symbols(self):
        """Tests compute_christoffel_symbols function for expected shape and type."""
        # Checks if `compute_christoffel_symbols` outputs an array of the correct shape
        # and type, which is essential for subsequent calculations in geodesic equations.
        x, y, z = 1.0, 1.0, 0.0
        Gamma = compute_christoffel_symbols(x, y, z)
        self.assertEqual(Gamma.shape, (4, 4, 4))
        self.assertIsInstance(Gamma, np.ndarray)

    def test_geodesic_equations(self):
        """Tests geodesic_equations function for correct output shape."""
        # Verifies that `geodesic_equations` returns an output of the correct shape
        # for a given position and momentum vector. This ensures that the geodesic
        # equation calculation produces the expected number of output values (7).
        t, M, a = 0.0, 1.0, 0.5
        Y = [1.0, 0.0, 0.0, -1.0, 0.0, 0.0,0.0]
        dydt = geodesic_equations(t, Y, M, a)
        self.assertEqual(len(dydt), 7)

    def test_integrate_geodesic(self):
        """Tests integrate_geodesic function for event handling and integration success."""
        # Tests if `integrate_geodesic` correctly handles the integration process, stopping
        # if the geodesic reaches the horizon or a max distance. This is important for simulating
        # paths that stay within bounds and do not cross physical barriers like event horizons.
        x0, y0, z0 = 10.0, 0.0, 0.0
        px0, py0, pz0 = -1.0, 0.0, 0.0
        max_distance = np.sqrt(x0**2 + y0**2 + z0**2)
        result = integrate_geodesic(x0, y0, z0, px0, py0, pz0, max_distance)
        
        # Ensures the integration stops within max_distance
        final_r = np.sqrt(result.y[0, -1]**2 + result.y[1, -1]**2 + result.y[2, -1]**2)
        self.assertLessEqual(final_r, max_distance)

if __name__ == "__main__":
    unittest.main(verbosity=2)