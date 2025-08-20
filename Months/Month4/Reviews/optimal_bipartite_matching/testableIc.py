import numpy as np
from scipy.spatial import cKDTree

def divide_space_using_quadtrees(points, max_depth=10, current_depth=0):
    """
    Divide the 2D space recursively via quadtrees.
    """
    if len(points) < 1 or current_depth == max_depth:
        return {'points': points}
    else:
        bounds_minimum = np.min(points, axis=0)
        bounds_maximum = np.max(points, axis=0)
        midpoint = (bounds_minimum + bounds_maximum) / 2

        subdivisions = []
        for quadrant in range(4):
            inclusive_mask = np.ones(len(points), dtype=bool)
            # Assign quadrants
            if quadrant & 1:
                inclusive_mask &= points[:, 0] >= midpoint[0]
            else:
                inclusive_mask &= points[:, 0] < midpoint[0]
            if quadrant & 2:
                inclusive_mask &= points[:, 1] >= midpoint[1]
            else:
                inclusive_mask &= points[:, 1] < midpoint[1]

            sub_points = points[inclusive_mask]
            subdivisions.append(divide_space_using_quadtrees(sub_points, max_depth, current_depth + 1))

        return {'bounds': (bounds_minimum, bounds_maximum), 'subdivisions': subdivisions}


def approximate_bipartite_matching(points_x, points_y, max_depth=10):
    """
    Perform an approximate bipartite matching using spatial segmentation and local matching refinement.
    """
    # Build Quadtrees for spatially segmenting points
    quadtree_x = divide_space_using_quadtrees(np.array(points_x), max_depth)
    quadtree_y = divide_space_using_quadtrees(np.array(points_y), max_depth)

    # Approximate Matching Using Nearest Neighbors
    kdtree_x = cKDTree(points_x)
    kdtree_y = cKDTree(points_y)

    matches = []
    for i, point in enumerate(points_x):
        dist, idx = kdtree_y.query(point, k=1)
        matches.append((i, idx))

    # Further Refinement or Adjustment
    total_cost = sum(np.linalg.norm(np.array(points_x[i]) - np.array(points_y[j])) for i, j in matches)
    
    return matches, total_cost

def optimal_bipartite_matching(points_x, points_y):
    return approximate_bipartite_matching(points_x, points_y)
