import unittest
from testableIC import omega_change_threshold_x, omega_change_threshold_y, omega_change_threshold_z,activation_interval_x, activation_interval_y, activation_interval_z

class TestControlSettings(unittest.TestCase):
    def test_omega_thresholds_and_activation_intervals_distinct_x_y(self):
        self.assertNotEqual(omega_change_threshold_x, omega_change_threshold_y)
        self.assertNotEqual(activation_interval_x, activation_interval_y)

    def test_omega_thresholds_and_activation_intervals_distinct_x_z(self):
        self.assertNotEqual(omega_change_threshold_x, omega_change_threshold_z)
        self.assertNotEqual(activation_interval_x, activation_interval_z)

    def test_omega_thresholds_and_activation_intervals_distinct_y_z(self):
        self.assertNotEqual(omega_change_threshold_y, omega_change_threshold_z)
        self.assertNotEqual(activation_interval_y, activation_interval_z)

if __name__ == '__main__':
    unittest.main(verbosity=2)