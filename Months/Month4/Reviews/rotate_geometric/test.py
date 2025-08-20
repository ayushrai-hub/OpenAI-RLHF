import unittest
import numpy as np
from testable import *

class TestLineRotations(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Expected values
        cls.theta = np.deg2rad(45)  
        cls.axis = np.array([0, 0, 1])  
        cls.point1 = np.array([1, 0, 0])
        cls.point2 = np.array([0, 1, 0])
        cls.expected_point1 = np.array([np.sqrt(2)/2, np.sqrt(2)/2, 0])
        cls.expected_point2 = np.array([-np.sqrt(2)/2, np.sqrt(2)/2, 0])

    def test_rotate_geometric(self):
        # Test Euclidean Geometric Algebra rotation function
        rotated_point1_ga = rotate_geometric(self.point1, self.axis, self.theta)
        rotated_point2_ga = rotate_geometric(self.point2, self.axis, self.theta)
        np.testing.assert_almost_equal(rotated_point1_ga, self.expected_point1, decimal=5)
        np.testing.assert_almost_equal(rotated_point2_ga, self.expected_point2, decimal=5)

    def test_rotate_conformal(self):
        # Test Conformal Geometric Algebra rotation function
        rotated_point1_cga = rotate_conformal(self.point1, self.axis, self.theta)
        rotated_point2_cga = rotate_conformal(self.point2, self.axis, self.theta)
        np.testing.assert_almost_equal(rotated_point1_cga, self.expected_point1, decimal=5)
        np.testing.assert_almost_equal(rotated_point2_cga, self.expected_point2, decimal=5)

    def test_rotate_euler(self):
        # Test Euler angle rotation function
        rotated_point1_euler = rotate_euler(self.point1, self.theta)
        rotated_point2_euler = rotate_euler(self.point2, self.theta)
        np.testing.assert_almost_equal(rotated_point1_euler, self.expected_point1, decimal=5)
        np.testing.assert_almost_equal(rotated_point2_euler, self.expected_point2, decimal=5)

    def test_rotate_matrix(self):
        # Test Rotation matrix function
        rotated_point1_matrix = rotate_matrix(self.point1, self.axis, self.theta)
        rotated_point2_matrix = rotate_matrix(self.point2, self.axis, self.theta)
        np.testing.assert_almost_equal(rotated_point1_matrix, self.expected_point1, decimal=5)
        np.testing.assert_almost_equal(rotated_point2_matrix, self.expected_point2, decimal=5)

    def test_rotate_quaternion(self):
        # Test Quaternion-based rotation function
        rotated_point1_quat = rotate_quaternion(self.point1, self.axis, self.theta)
        rotated_point2_quat = rotate_quaternion(self.point2, self.axis, self.theta)
        np.testing.assert_almost_equal(rotated_point1_quat, self.expected_point1, decimal=5)
        np.testing.assert_almost_equal(rotated_point2_quat, self.expected_point2, decimal=5)

if __name__ == "__main__":
    unittest.main(verbosity=2)
