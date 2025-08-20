from shapely.geometry import Point
from shapely.strtree import STRtree

# Original list of geometries
points = [Point(0, 0), Point(1, 1), Point(2, 2), Point(3, 3)]

# Store geometries with their indices
indexed_geometries = [(point, i) for i, point in enumerate(points)]

# Create the STRtree with the geometries (ignoring indices for the tree itself)
tree = STRtree([item[0] for item in indexed_geometries])

# Query for the nearest point
query_point = Point(1.5, 1.5)

# Find the nearest geometry
nearest_geom_index = tree.nearest(query_point)
nearest_geom = points[nearest_geom_index]

# Find the corresponding index
nearest_index = next(index for geom, index in indexed_geometries if geom.equals(nearest_geom))

print(f"The nearest geometry to {query_point} is at index {nearest_index} in the original list.")

# Additional output for verification
print("\nDetailed output:")
print(f"Query point: {query_point}")
print(f"Nearest point: {nearest_geom}")
print(f"Nearest point index: {nearest_index}")

print("\nDistances from query point to all points:")
for i, point in enumerate(points):
    distance = query_point.distance(point)
    print(f"  To point at index {i}: {distance}")