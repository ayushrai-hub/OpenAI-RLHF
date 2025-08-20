
import trimesh
import numpy as np

def main(mesh_path):
    # Load your mesh
    mesh = trimesh.load(mesh_path)

    # Check if the mesh is watertight (closed)
    is_closed = mesh.is_watertight

    # Identifying boundary edges
    # Edges that belong to only one triangle are considered boundary edges
    edges_unique = mesh.edges_unique
    edges_face = mesh.edges_face
    boundary_edges = edges_unique[np.sum(edges_face == -1, axis=1) == 1]

    # Finding sharp edges
    # Get the angles between the normals of adjacent faces
    face_adjacency_angles = mesh.face_adjacency_angles
    angle_threshold = np.radians(45)  # Convert 45 degrees to radians
    sharp_edges = mesh.face_adjacency_edges[face_adjacency_angles > angle_threshold]

    # Extract vertices from sharp edges
    sharp_vertices = mesh.vertices[sharp_edges.flatten()]
    
    return is_closed, boundary_edges, sharp_vertices
