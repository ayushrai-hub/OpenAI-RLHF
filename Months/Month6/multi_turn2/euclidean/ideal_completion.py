import numpy as np
from scipy.optimize import linear_sum_assignment
from typing import List, Tuple

def optimal_bipartite_matching(points_x: List[Tuple[float, float]], 
                               points_y: List[Tuple[float, float]]) -> Tuple[List[Tuple[int, int]], float]:
    if len(points_x) != len(points_y):
        raise ValueError("Both input point sets must have the same number of points.")
    
    num_points = len(points_x)
    cost_matrix = np.zeros((num_points, num_points))
    
    for i, (x1, y1) in enumerate(points_x):
        for j, (x2, y2) in enumerate(points_y):
            cost_matrix[i, j] = np.hypot(x1 - x2, y1 - y2)
    
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    matches = list(zip(row_ind.tolist(), col_ind.tolist()))
    total_cost = cost_matrix[row_ind, col_ind].sum()
    
    return matches, total_cost
