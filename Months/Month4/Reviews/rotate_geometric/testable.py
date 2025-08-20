import numpy as np
from clifford import Cl
from clifford.g3c import *
e1, e2, e3 = layout.blades['e1'], layout.blades['e2'], layout.blades['e3']

# Euler Angles Rotation
def rotate_euler(point, theta):
    Rz = np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta),  np.cos(theta), 0],
        [0, 0, 1]
    ])
    return Rz @ point

# Rotation Matrix Rotation (Rodrigues' formula)
def rotate_matrix(point, axis, theta):
    axis = axis / np.linalg.norm(axis)
    K = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])
    R = np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * np.dot(K, K)
    return R @ point

# Quaternion-based Rotation
def rotate_quaternion(point, axis, theta):
    axis = axis / np.linalg.norm(axis)
    q0 = np.cos(theta / 2)
    q1, q2, q3 = np.sin(theta / 2) * axis
    q = np.array([q0, q1, q2, q3])
    
    # Rotation via quaternion multiplication
    q_conj = np.array([q0, -q1, -q2, -q3])
    
    def quaternion_mult(q1, q2):
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        return np.array([
            w1*w2 - x1*x2 - y1*y2 - z1*z2,
            w1*x2 + x1*w2 + y1*z2 - z1*y2,
            w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2
        ])
    
    point_q = np.array([0, point[0], point[1], point[2]])
    rotated_q = quaternion_mult(quaternion_mult(q, point_q), q_conj)
    
    return rotated_q[1:]

# Geometric Algebra Rotation (Euclidean and Conformal)
def rotate_geometric(point, axis, theta):
    # Axis-aligned bivector for rotation
    bivector = np.sin(theta / 2) * (e1^e2)
    R = np.exp(-bivector)
    p = point[0]*e1 + point[1]*e2 + point[2]*e3
    p_rot = R * p * ~R
    return np.array([p_rot(e1), p_rot(e2), p_rot(e3)])

# Conformal Geometric Algebra alias
rotate_conformal = rotate_geometric
