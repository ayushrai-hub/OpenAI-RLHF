from shapely.geometry import Point
from shapely.strtree import STRtree
import numpy as np

class IndexedPoint:
    def __init__(self, point, index):
        self.point = point
        self.index = index

# Create sample points
points = [Point(0, 0), Point(1, 1), Point(2, 2), Point(3, 3)]

# Create IndexedPoint objects
indexed_points = [IndexedPoint(point, i) for i, point in enumerate(points)]

# Build the STRtree with IndexedPoint objects
tree = STRtree([ip.point for ip in indexed_points])

# Custom distance function for nearest neighbor search
def indexed_distance(item, query):
    return item.point.distance(query)

# Query point
query_point = Point(1.5, 1.5)

# Find the nearest point and its index
nearest = tree.nearest(query_point, indexed_distance, return_distance=True)
nearest_indexed_point = indexed_points[tree.geometries.index(nearest[0])]

print(f"Nearest point to {query_point}:")
print(f"  Coordinates: {nearest_indexed_point.point.coords[0]}")
print(f"  Original index: {nearest_indexed_point.index}")
print(f"  Distance: {nearest[1]:.2f}")

# Demonstration of finding k-nearest neighbors
k = 3
k_nearest = tree.nearest(query_point, indexed_distance, return_distance=True, all_matches=True, max_distance=np.inf)[:k]

print(f"\n{k} nearest neighbors:")
for geom, dist in k_nearest:
    idx = indexed_points[tree.geometries.index(geom)].index
    print(f"  Index: {idx}, Distance: {dist:.2f}")