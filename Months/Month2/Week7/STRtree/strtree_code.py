# File: nearest_point_finder.py

from shapely.geometry import Point
from shapely.strtree import STRtree

def find_nearest_point_index(points, query_point):
    """
    Find the index of the nearest point in the list to the query point.
    
    :param points: List of Point objects
    :param query_point: Point object to query against
    :return: Index of the nearest point in the original list
    """
    tree = STRtree(points)
    tree_index = int(tree.nearest(query_point))
    return tree_index

if __name__ == "__main__":
    points = [Point(0, 0), Point(1, 1), Point(2, 2), Point(3, 3)]
    query_point = Point(1.5, 1.5)
    result = find_nearest_point_index(points, query_point)
    print(f"The nearest geometry to {query_point} is at index {result} in the original list.")