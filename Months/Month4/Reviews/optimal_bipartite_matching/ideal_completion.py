# ideal_completion.py

import numpy as np
from scipy.optimize import linear_sum_assignment

def optimal_bipartite_matching(points_x, points_y):

    cost_matrix = np.linalg.norm(np.array(points_x)[:, np.newaxis] - np.array(points_y), axis=2)
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    matches = list(zip(row_ind, col_ind))
    total_cost = cost_matrix[row_ind, col_ind].sum()
    return matches, total_cost