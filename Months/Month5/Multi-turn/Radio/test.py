import unittest
import numpy as np
from try_ideal import RadioInterferometerSimulation

class TestRadioInterferometerSimulation(unittest.TestCase):

    def setUp(self):
        self.sim = RadioInterferometerSimulation()
        self.delta_t1, self.delta_t2 = self.sim.generate_timing_errors()
        self.phi1, self.phi2, self.delta_phi = self.sim.calculate_phase_errors(self.delta_t1, self.delta_t2)
        self.s1, self.s2 = self.sim.simulate_signals(self.phi1, self.phi2)
        self.V12, self.amp_V12, self.phase_V12 = self.sim.calculate_visibility(self.s1, self.s2)

    # Test to check the generation of timing errors
    # its important to test because it verifies that timing errors are generated with correct properties
    def test_generate_timing_errors(self):
        self.assertEqual(len(self.delta_t1), len(self.sim.t))
        self.assertEqual(len(self.delta_t2), len(self.sim.t))
        self.assertAlmostEqual(np.std(self.delta_t1), self.sim.sigma_delta_t, places=10)
        self.assertAlmostEqual(np.std(self.delta_t2), self.sim.sigma_delta_t, places=10)

    # Test to check the calculation of phase errors
    # its important to ensure phase errors are correctly calculated
    def test_calculate_phase_errors(self):
        expected_phi1 = 2 * np.pi * self.sim.f * self.delta_t1
        expected_phi2 = 2 * np.pi * self.sim.f * self.delta_t2
        np.testing.assert_array_almost_equal(self.phi1, expected_phi1)
        np.testing.assert_array_almost_equal(self.phi2, expected_phi2)
        np.testing.assert_array_almost_equal(self.delta_phi, self.phi1 - self.phi2)

    # Test the  simulation of radio signals
    # Its  important to check that signals are simulated correctly with phase errors for radio signal simulation
    def test_simulate_signals(self):
        self.assertEqual(len(self.s1), len(self.sim.t))
        self.assertEqual(len(self.s2), len(self.sim.t))
        self.assertTrue(np.iscomplexobj(self.s1))
        self.assertTrue(np.iscomplexobj(self.s2))

    # Test to calculate visibility
    # Its imoprtant to verify that visibility is correctly calculated from signals
    def test_calculate_visibility(self):
        expected_V12 = self.s1 * np.conj(self.s2)
        np.testing.assert_array_almost_equal(self.V12, expected_V12)
        expected_amp_V12 = np.abs(np.mean(expected_V12))
        expected_phase_V12 = np.angle(np.mean(expected_V12))
        self.assertAlmostEqual(self.amp_V12, expected_amp_V12)
        self.assertAlmostEqual(self.phase_V12, expected_phase_V12)

    # Test to check the  visualization of phase errors
    # This test ensures that the phase error plots are generated without errors   and graphs are plotted.
    def test_visualize_phase_errors(self):
        try:
            self.sim.visualize_phase_errors(self.delta_phi, self.V12)
        except Exception as e:
            self.fail(f'visualize_phase_errors raised an exception: {e}')

    # Test the synthesis of image
    # Its important because image  synthize will mae sure image  is interpretable
    def test_synthesize_image(self):
        try:
            self.sim.synthesize_image(self.V12)
        except Exception as e:
            self.fail(f'synthesize_image raised an exception: {e}')


if __name__ == '__main__':
    unittest.main(verbosity=2)