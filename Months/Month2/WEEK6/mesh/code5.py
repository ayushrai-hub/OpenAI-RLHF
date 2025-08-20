import numpy as np
import trimesh

# Create mock data for a simple cube
vertices = np.array([
    [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
    [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
])

faces = np.array([
    [0, 1, 2], [0, 2, 3],  # Bottom face
    [4, 5, 6], [4, 6, 7],  # Top face
    [0, 4, 7], [0, 7, 3],  # Left face
    [1, 5, 6], [1, 6, 2],  # Right face
    [0, 1, 5], [0, 5, 4],  # Front face
    [3, 2, 6], [3, 6, 7]   # Back face
])

# Create a trimesh object from the mock data
mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

# Check if the mesh is watertight (closed)
is_closed = mesh.is_watertight
print(f"The mesh is {'closed' if is_closed else 'not closed'}.")

# Identify boundary edges
edges_unique = mesh.edges_unique
edges_face = mesh.edges_face
boundary_edges = edges_unique[np.sum(edges_face == -1, axis=1) == 1]
print(f"Number of boundary edges: {len(boundary_edges)}")

# Extract boundary vertices
boundary_vertices = np.unique(boundary_edges)
print(f"Number of boundary vertices: {len(boundary_vertices)}")

# Detect sharp edges
angle_threshold = np.radians(45)  # 45 degrees in radians
face_adjacency_angles = mesh.face_adjacency_angles
sharp_edge_indices = np.where(face_adjacency_angles > angle_threshold)[0]
sharp_edges = mesh.face_adjacency_edges[sharp_edge_indices]
print(f"Number of sharp edges: {len(sharp_edges)}")

# Extract sharp vertices
sharp_vertices = np.unique(sharp_edges)
print(f"Number of sharp vertices: {len(sharp_vertices)}")

# Visualize the results
mesh.visual.face_colors = [200, 200, 250, 100]  # Light blue for the mesh
sharp_points = mesh.vertices[sharp_vertices]
sharp_cloud = trimesh.points.PointCloud(sharp_points, colors=[255, 0, 0, 255])  # Red for sharp points
scene = trimesh.Scene([mesh, sharp_cloud])
scene.show()

# The mock data creates a simple cube mesh.
# Vertices array defines 8 corners of the cube.
# Faces array defines 12 triangles (2 for each face of the cube).

# The mesh is checked for being watertight (closed).
# For a cube, it should be closed with no boundary edges.

# Sharp edges are detected using the angle between adjacent faces.
# All edges of a cube should be detected as sharp (90-degree angles).

# The results are visualized, with sharp vertices highlighted in red.
# For a cube, all vertices should be considered sharp.