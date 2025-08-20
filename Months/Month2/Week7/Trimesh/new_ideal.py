import trimesh
import numpy as np
import matplotlib.pyplot as plt

def analyze_mesh(vertices, faces, angle_threshold_degrees=45):
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    
    # Check if the mesh is closed
    is_closed = mesh.is_watertight
    print(f"The mesh is {'closed' if is_closed else 'not closed'}.")
    
    # Find boundary edges
    boundary_edges = mesh.edges_unique[mesh.edges_unique_length == 1]
    print(f"Number of boundary edges: {len(boundary_edges)}")
    
    # Find sharp edges
    angle_threshold = np.radians(angle_threshold_degrees)
    face_adjacency_angles = mesh.face_adjacency_angles
    sharp_edges = mesh.face_adjacency_edges[face_adjacency_angles > angle_threshold]
    print(f"Number of sharp edges: {len(sharp_edges)}")
    
    # Extract vertices from sharp edges
    sharp_vertices = np.unique(sharp_edges.flatten())
    print(f"Number of sharp vertices: {len(sharp_vertices)}")
    
    # Visualize the results
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot all vertices
    ax.scatter(mesh.vertices[:, 0], mesh.vertices[:, 1], mesh.vertices[:, 2], c='b', s=10, label='All Vertices')
    
    # Plot sharp vertices
    ax.scatter(mesh.vertices[sharp_vertices, 0], mesh.vertices[sharp_vertices, 1], mesh.vertices[sharp_vertices, 2], c='r', s=50, label='Sharp Vertices')
    
    # Plot edges
    for edge in mesh.edges_unique:
        ax.plot(mesh.vertices[edge, 0], mesh.vertices[edge, 1], mesh.vertices[edge, 2], 'k-', linewidth=0.5)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()
    plt.title('3D Mesh with Sharp Vertices Highlighted')
    plt.show()
    
    return is_closed, boundary_edges, sharp_edges, sharp_vertices