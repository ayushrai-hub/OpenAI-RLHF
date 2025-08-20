import trimesh
import numpy as np

# Load your mesh
mesh = trimesh.load('path_to_your_mesh_file.obj')

# Check if the mesh is watertight (closed)
is_closed = mesh.is_watertight
print(f"The mesh is {'closed' if is_closed else 'not closed'}.")

# Identifying boundary edges
# Edges that belong to only one triangle are considered boundary edges
edges_unique = mesh.edges_unique
edges_face = mesh.edges_face
boundary_edges = edges_unique[np.sum(edges_face == -1, axis=1) == 1]

print(f"Boundary edges: {boundary_edges}")

# Finding sharp edges
# Get the angles between the normals of adjacent faces
face_adjacency_angles = mesh.face_adjacency_angles
angle_threshold = np.radians(45)  # Convert 45 degrees to radians
sharp_edges = mesh.face_adjacency_edges[face_adjacency_angles > angle_threshold]

# Extract vertices from sharp edges
sharp_vertices = mesh.vertices[sharp_edges.flatten()]
print(f"Sharp vertices: {sharp_vertices}")
