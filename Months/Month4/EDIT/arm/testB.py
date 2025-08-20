import unittest
import numpy as np
from ideal_completion import ikine, fkine, joint_blended, cartesian_blended, min_line_point_distance, min_robot_point_distance

class TestMotionPlanningTasks(unittest.TestCase):

    def test_joint_blended_output_shapes(self):
        # Test that joint_blended returns the correct output shapes
        p_start = np.array([0, 0, 0])
        p_finish = np.array([100, 0, 0])
        num_points = 5

        pos_traj, angle_traj = joint_blended(p_start, p_finish, num_points)

        self.assertEqual(pos_traj.shape, (num_points, 3))
        self.assertEqual(angle_traj.shape, (num_points, 3))

    def test_cartesian_blended_linear_interpolation(self):
        # Test that cartesian_blended performs correct linear interpolation
        p_start = np.array([0, 0, 0])
        p_finish = np.array([100, 100, 0])
        num_points = 5

        pos_traj, _ = cartesian_blended(p_start, p_finish, num_points)

        expected_positions = np.array([
            [0, 0, 0],
            [25, 25, 0],
            [50, 50, 0],
            [75, 75, 0],
            [100, 100, 0]
        ])

        np.testing.assert_array_almost_equal(pos_traj, expected_positions)

    def test_min_line_point_distance_calculation(self):
        # Test min_line_point_distance with known values
        pt1 = np.array([0, 0, 0])
        pt2 = np.array([0, 10, 0])
        obs = np.array([5, 5, 0])

        distance = min_line_point_distance(pt1, pt2, obs)

        # The shortest distance should be 5 units
        self.assertAlmostEqual(distance, 5.0)

    def test_min_robot_point_distance_with_zero_angles(self):
        # Test min_robot_point_distance when robot is at zero angles
        angles = np.array([0, 0, 0])
        obs = np.array([200, 0, 0])  # At maximum reach along x-axis

        distance = min_robot_point_distance(angles, obs)

        # The end effector is at [200, 0, 0], so distance should be zero
        self.assertAlmostEqual(distance, 0.0)

    def test_ikine_and_fkine_consistency(self):
        # Test that applying fkine to the output of ikine returns the original position
        positions = [
            np.array([150, 50, 0]),
            np.array([50, 150, 0]),
            np.array([100, 100, 0])
        ]

        for position in positions:
            angles = ikine(position)
            reconstructed_position = fkine(angles)
            np.testing.assert_array_almost_equal(reconstructed_position, position, decimal=5)

    def test_ikine_unreachable_position_raises_error(self):
        # Test that ikine raises an error for unreachable positions
        position = np.array([500, 0, 0])  # Beyond maximum reach

        with self.assertRaises(ValueError):
            angles = ikine(position)

if __name__ == '__main__':
    unittest.main(verbosity=2)