# ideal_completion.py

import numpy as np
from clifford import Cl
from scipy.spatial.transform import Rotation as R

# Initialize 3D geometric algebra for Euclidean and conformal rotations
layout, blades = Cl(3)
e1, e2, e3 = blades['e1'], blades['e2'], blades['e3']

# Define original lines
point1 = np.array([1, 0, 0])
point2 = np.array([0, 1, 0])
lines = [(point1, point2)]

# Rotation specifics
theta = np.deg2rad(45)  # 45 degrees in radians
axis = np.array([0, 0, 1])  # z-axis

# Euclidean Geometric Algebra rotation
def rotate_geometric(point, axis, theta):
    axis = axis / np.linalg.norm(axis)
    B = axis[0] * e2 * e3 + axis[1] * e3 * e1 + axis[2] * e1 * e2
    rotor = np.cos(theta / 2) - np.sin(theta / 2) * B  
    p = point[0] * e1 + point[1] * e2 + point[2] * e3
    rotated_point = rotor * p * ~rotor
    return np.array([float(rotated_point[e1]), float(rotated_point[e2]), float(rotated_point[e3])])
  
# Conformal Geometric Algebra rotation is similar to Euclidean here
rotate_conformal = rotate_geometric

# Rotation using Euler angles
def rotate_euler(point, theta):
    Rz = np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta),  np.cos(theta), 0],
        [0, 0, 1]
    ])
    return Rz @ point

# Rotation matrix (Rodrigues' formula)
def rotate_matrix(point, axis, theta):
    axis = axis / np.linalg.norm(axis)
    K = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])
    R = np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * np.dot(K, K)
    return R @ point

# Quaternion-based rotation
def rotate_quaternion(point, axis, theta):
    r = R.from_rotvec(theta * axis)
    return r.apply(point)