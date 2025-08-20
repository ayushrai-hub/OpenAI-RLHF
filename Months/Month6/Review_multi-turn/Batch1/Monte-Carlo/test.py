import unittest
import numpy as np
from ideal_completion import simulate_photon_attenuation, mu_a, mu_s, L, delta_z, num_photons, num_sets  

class TestPhotonAttenuationSimulation(unittest.TestCase):
    
    def setUp(self):
        self.mu_a = mu_a
        self.mu_s = mu_s
        self.L = L
        self.delta_z = delta_z
        self.num_photons = num_photons
        self.num_sets = num_sets

    def test_no_scattering(self):
        # Test to verify that the scattering coefficient is zero.
        self.assertEqual(self.mu_s, 0)
    
    def test_fraction_absorbed_range(self):
        # Test to verify that the fraction absorbed is within the range [0, 1].
        z_midpoints, fraction_absorbed, theoretical_fraction = simulate_photon_attenuation(
            self.mu_a, self.mu_s, self.L, self.delta_z, self.num_photons, self.num_sets
        )
        self.assertTrue(np.all((fraction_absorbed >= 0) & (fraction_absorbed <= 1)))

    def test_monotonic_theoretical_fraction(self):
        # Test to verify that the theoretical absorption fraction decreases with depth.
        z_midpoints, fraction_absorbed, theoretical_fraction = simulate_photon_attenuation(
            self.mu_a, self.mu_s, self.L, self.delta_z, self.num_photons, self.num_sets
        )
        self.assertTrue(np.all(np.diff(theoretical_fraction) <= 0))
    
    def test_average_fraction_matches_theory(self):
        # Test to verify that the simulated fraction of absorbed photons closely matches the theoretical values.
        z_midpoints, fraction_absorbed, theoretical_fraction = simulate_photon_attenuation(
            self.mu_a, self.mu_s, self.L, self.delta_z, self.num_photons, self.num_sets
        )
        max_allowed_difference = 0.05
        max_difference = np.abs(fraction_absorbed - theoretical_fraction).max()
        self.assertLessEqual(max_difference, max_allowed_difference)

    def test_nonzero_absorption(self):
        # Test to verify that some photons are absorbed (nonzero total absorption).
        z_midpoints, fraction_absorbed, theoretical_fraction = simulate_photon_attenuation(
            self.mu_a, self.mu_s, self.L, self.delta_z, self.num_photons, self.num_sets
        )
        total_absorbed = fraction_absorbed.sum()
        self.assertGreater(total_absorbed, 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)