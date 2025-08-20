from shapely.geometry import Point

class IndexedGeometries:
    def __init__(self, geometries):
        self.geometries = geometries
        self.indices = list(range(len(geometries)))

    def nearest(self, query_geometry):
        if not self.geometries:
            return None, None

        # Find the nearest geometry using minimum distance
        distances = [query_geometry.distance(geom) for geom in self.geometries]
        nearest_index = min(range(len(distances)), key=distances.__getitem__)
        nearest_geometry = self.geometries[nearest_index]

        return nearest_geometry, self.indices[nearest_index]

# Example usage
points = [Point(0, 0), Point(1, 1), Point(2, 2), Point(3, 3)]
indexed_geometries = IndexedGeometries(points)

query_point = Point(1.5, 1.5)
nearest_geometry, nearest_index = indexed_geometries.nearest(query_point)

if nearest_geometry is not None and nearest_index is not None:
    print(f"The nearest geometry to {query_point} is {nearest_geometry} at index {nearest_index} in the original list.")
else:
    print(f"No nearest geometry found for {query_point}")