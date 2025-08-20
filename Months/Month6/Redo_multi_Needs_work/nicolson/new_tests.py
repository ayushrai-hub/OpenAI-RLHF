# Updated tests

import unittest
import numpy as np
from ideal_completion import crank_nicolson_2D_sphere

class TestPythonCode(unittest.TestCase):
    def setUp(self):
        # Common test parameters
        self.t_limit = 10.0  # seconds
        self.radius = 1.0  # meters
        self.theta = np.pi  # radians
        self.d_radius = 0.05  # meters
        self.d_theta = np.pi / 16  # radians
        self.d_time = 0.1  # seconds
        self.beta = 1e-5  # m^2/s
        self.Initial_Temp = 20.0  # degrees
        self.Energy = 500.0  # Joules
        self.impulse_time = 1.0  # seconds
        self.conv = 5.0  # convection coefficient
        self.specific_heat = 900.0  # J/kg°C
        self.density = 7800.0  # kg/m³

    def test_basic_execution(self):
        # It tests that the function executes without raising ValueError.
        try:
            temps, times = crank_nicolson_2D_sphere(
                self.t_limit, self.radius, self.theta, self.d_radius, 
                self.d_theta, self.d_time, self.beta, self.Initial_Temp, 
                self.Energy, self.impulse_time, self.conv, self.specific_heat,
                self.density
            )
            self.assertIsInstance(temps, np.ndarray)
            self.assertIsInstance(times, np.ndarray)
        except ValueError:
            self.fail("ValueError was raised unexpectedly")

    def test_temperature_normalization(self):
        # It tests that temperatures are properly normalized between 0 and 1.
        temps, _ = crank_nicolson_2D_sphere(
            self.t_limit, self.radius, self.theta, self.d_radius, 
            self.d_theta, self.d_time, self.beta, self.Initial_Temp, 
            self.Energy, self.impulse_time, self.conv, self.specific_heat,
            self.density
        )
        self.assertTrue(np.all(temps >= 0.0))
        self.assertTrue(np.all(temps <= 1.0))

    def test_time_array_consistency(self):
        # It tests that the time array is generated correctly.
        _, times = crank_nicolson_2D_sphere(
            self.t_limit, self.radius, self.theta, self.d_radius, 
            self.d_theta, self.d_time, self.beta, self.Initial_Temp, 
            self.Energy, self.impulse_time, self.conv, self.specific_heat,
            self.density
        )
        expected_times = np.arange(0, self.t_limit + self.d_time, self.d_time)
        np.testing.assert_array_almost_equal(times, expected_times)

    def test_grid_dimensions(self):
        # It tests that the temperature grid has correct dimensions.
        temps, times = crank_nicolson_2D_sphere(
            self.t_limit, self.radius, self.theta, self.d_radius, 
            self.d_theta, self.d_time, self.beta, self.Initial_Temp, 
            self.Energy, self.impulse_time, self.conv, self.specific_heat,
            self.density
        )
        r_points = max(2, int(np.round(self.radius / self.d_radius)) + 1)
        theta_points = max(2, int(np.round(self.theta / self.d_theta)) + 1)
        time_points = len(np.arange(0, self.t_limit + self.d_time, self.d_time))
        
        self.assertEqual(temps.shape, (time_points, r_points, theta_points))

if __name__ == "__main__":
    unittest.main(verbosity=2)