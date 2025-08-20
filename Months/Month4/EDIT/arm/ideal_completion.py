# ideal_completion.py

import numpy as np
# Constants for a hypothetical 3DOF planar robot arm
# Example link lengths
L1, L2, L3 = 100, 100, 100  # in millimetres

def ikine(position):
    """
    Inverse kinematics function that computes joint angles given an end effector position.
    """
    x, y, z = position
    d = np.hypot(x, y)

    # Check if the point is within reach
    if d > (L1 + L2) or d < abs(L1 - L2):
        raise ValueError("Target position is outside the robot's reach")

    cos_angle2 = (d**2 - L1**2 - L2**2) / (2 * L1 * L2)
    sin_angle2 = np.sqrt(1 - cos_angle2**2)
    angle2 = np.arctan2(sin_angle2, cos_angle2)

    k1 = L1 + L2 * cos_angle2
    k2 = L2 * sin_angle2
    angle1 = np.arctan2(y, x) - np.arctan2(k2, k1)

    angle3 = 0

    return np.array([angle1, angle2, angle3])


def fkine(angles):
    """
    Forward kinematics function that computes an end effector position given the joint angles.

    Parameters
    ----------
    angles
        A numpy array of shape (3,) representing the joint angles in radians

    Returns
    -------
    position
        A numpy array of shape (3,) representing the xyz coordinates in millimetres of the end effector
    """
    angle1, angle2, angle3 = angles
    # Calculate position of the end effector using FK equations
    x = L1 * np.cos(angle1) + L2 * np.cos(angle1 + angle2)
    y = L1 * np.sin(angle1) + L2 * np.sin(angle1 + angle2)
    # Assuming planar movement, z is constant or zero
    z = 0  

    return np.array([x, y, z])

# --------- Task 1 ---------- #

def joint_blended(p_start, p_finish, num_points):
    """
    Calculate a joint blended path between two locations in 3D space

    Parameters
    ----------
    p_start
        A numpy array of shape (3,) representing the initial position in millimetres
    p_finish
        A numpy array of shape (3,) representing the target position in millimetres
    num_points
        Total number of waypoints in the path

    Returns
    -------
    pos_traj
        A numpy array of shape (num_points, 3) providing the end effector location in millimetres for every waypoint
    angle_traj
        A numpy array of shape (num_points, 3) providing the joint angles in radians for each waypoint
    """
    pos_traj = np.linspace(p_start, p_finish, num_points)
    angle_traj = np.array([ikine(p) for p in pos_traj])

    return pos_traj, angle_traj

# --------- Task 2 ---------- #

def cartesian_blended(p_start, p_finish, num_points):
    """
    Create a cartesian blended path between two positions in 3D space

    Parameters
    ----------
    p_start
        A numpy array of shape (3,) representing the initial position in millimetres
    p_finish
        A numpy array of shape (3,) representing the target position in millimetres
    num_points
        Total number of waypoints in the path

    Returns
    -------
    pos_traj
        A numpy array of shape (num_points, 3) providing the end effector location in millimetres for every waypoint
    angle_traj
        A numpy array of shape (num_points, 3) providing the joint angles in radians for each waypoint
    """
    pos_traj = np.linspace(p_start, p_finish, num_points)
    angle_traj = np.array([ikine(p) for p in pos_traj])

    return pos_traj, angle_traj

# --------- Task 3 ---------- #

def min_line_point_distance(pt1, pt2, obs):
    """
    Calculate the minimal distance between the line segment pt1pt2 and a point obstacle obs

    Parameters
    ----------
    pt1
        A numpy array of shape (3,) representing the xyz coordinates in millimetres of one endpoint of a line
    pt2
        A numpy array of shape (3,) representing the xyz coordinates in millimetres of the other endpoint of a line
    obs
        A numpy array of shape (3,) representing the xyz coordinates in millimetres of the point obstacle

    Returns
    -------
    shortest_distance
        A float indicating the shortest distance in millimetres from the line pt1pt2 to the obstacle obs
    """
    pt1pt2 = pt2 - pt1
    pt1obs = obs - pt1
    t = np.dot(pt1obs, pt1pt2) / np.dot(pt1pt2, pt1pt2)
    t = np.clip(t, 0, 1)
    closest_point = pt1 + t * pt1pt2
    shortest_distance = np.linalg.norm(obs - closest_point)

    return shortest_distance

# --------- Task 4 ---------- #

def min_robot_point_distance(angles, obs):
    """
    Calculate the minimal distance between the robot configuration defined by joint angles and a point obstacle obs

    Parameters
    ----------
    angles
        A numpy array of shape (3,) representing the robot's joint angles in radians
    obs
        A numpy array of shape (3,) representing the xyz coordinates in millimetres of the point obstacle

    Returns
    -------
    shortest_distance
        A float reflecting the shortest distance in millimetres from the point obs to the robot configuration
    """
    pos_robot = fkine(angles)
    shortest_distance = np.linalg.norm(pos_robot - obs)

    return shortest_distance