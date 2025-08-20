
import unittest
import numpy as np
from ideal_completion import fkine, ikine, joint_blended, cartesian_blended, min_line_point_distance, min_robot_point_distance, L1, L2

class TestRobotTasks(unittest.TestCase):

    def test_fkine(self):
        """Test the fkine function to ensure it computes the correct end-effector position given joint angles."""
        # Define some known joint angles
        angles = np.array([np.pi / 4, np.pi / 4, 0])  # Known angles for the test
        # Compute the end-effector position based on these angles
        computed_position = fkine(angles)
        # Expected position using trigonometry for the given angles (assuming L1 = L2 = 100)
        expected_x = L1 * np.cos(np.pi / 4) + L2 * np.cos(np.pi / 2)
        expected_y = L1 * np.sin(np.pi / 4) + L2 * np.sin(np.pi / 2)
        expected_position = np.array([expected_x, expected_y, 0])
        # Verify if the computed position is correct
        self.assertTrue(np.allclose(computed_position, expected_position, atol=1e-5),
                        "The computed end-effector position does not match the expected position.")
        
    def test_ikine_out_of_reach(self):
        """Test if ikine raises a ValueError when the target position is outside the robot's reach."""
        # Defining a point outside the robot's maximum range
        target_position = np.array([300, 300, 0])  # Out of robot's maximum range (L1 + L2 = 200)

        with self.assertRaises(ValueError) as context:
            ikine(target_position)
        
        self.assertEqual(str(context.exception), "Target position is outside the robot's reach")

    def test_joint_blended(self):
        """Test the joint_blended function to ensure it correctly computes the position and joint angles for a trajectory."""
        start_position = np.array([50, 50, 0])
        end_position = np.array([150, 100, 0])
        num_points = 5

        pos_traj, angle_traj = joint_blended(start_position, end_position, num_points)

        # Verify that the trajectory has the correct number of points
        self.assertEqual(pos_traj.shape, (num_points, 3), "Position trajectory shape mismatch")
        self.assertEqual(angle_traj.shape, (num_points, 3), "Angle trajectory shape mismatch")

        # Check if the start and end positions match the expected values
        self.assertTrue(np.allclose(pos_traj[0], start_position), "Start position in trajectory does not match")
        self.assertTrue(np.allclose(pos_traj[-1], end_position), "End position in trajectory does not match")

        # Check if the angles are calculated without errors (no NaNs)
        self.assertFalse(np.isnan(angle_traj).any(), "NaN values found in the angle trajectory")

    def test_cartesian_blended(self):
        """Test the cartesian_blended function to ensure it computes the correct positions and joint angles for a cartesian path."""
        start_position = np.array([60, 40, 0])
        end_position = np.array([120, 80, 0])
        num_points = 5

        pos_traj, angle_traj = cartesian_blended(start_position, end_position, num_points)

        # Verify the trajectory has the correct number of waypoints
        self.assertEqual(pos_traj.shape, (num_points, 3), "Position trajectory shape mismatch")
        self.assertEqual(angle_traj.shape, (num_points, 3), "Angle trajectory shape mismatch")

        # Check that the start and end positions are as expected
        self.assertTrue(np.allclose(pos_traj[0], start_position), "Start position in trajectory does not match")
        self.assertTrue(np.allclose(pos_traj[-1], end_position), "End position in trajectory does not match")

        # Check if the angles are computed correctly (no NaNs)
        self.assertFalse(np.isnan(angle_traj).any(), "NaN values found in the angle trajectory")

    def test_min_line_point_distance(self):
        """Test the min_line_point_distance function to ensure it correctly calculates the shortest distance from a point to a line segment."""
        pt1 = np.array([0, 0, 0])
        pt2 = np.array([100, 100, 0])
        obs = np.array([50, 50, 50])  # Point above the line in 3D

        shortest_distance = min_line_point_distance(pt1, pt2, obs)

        # Verify that the distance is correct for this geometry (pythagoras in 3D)
        expected_distance = np.sqrt(50**2)  # 50 units above the line
        self.assertAlmostEqual(shortest_distance, expected_distance, places=5, msg="Distance calculation is incorrect")

    def test_min_robot_point_distance(self):
        """Test the min_robot_point_distance function to ensure it correctly computes the distance from the robot's position to an obstacle."""
        angles = np.array([np.pi / 4, np.pi / 4, 0])  # Random valid angles
        obs = np.array([150, 150, 0])  # Obstacle in front of the robot

        shortest_distance = min_robot_point_distance(angles, obs)

        # Forward kinematics should return a valid end-effector position
        robot_position = fkine(angles)

        # Expected distance is the Euclidean distance between robot's end-effector and the obstacle
        expected_distance = np.linalg.norm(robot_position - obs)
        self.assertAlmostEqual(shortest_distance, expected_distance, places=5, msg="Robot-obstacle distance is incorrect")

if __name__ == '__main__':
    unittest.main(verbosity=2)
