import unittest
import numpy as np
import trimesh

class TestMeshAnalysis(unittest.TestCase):

    def setUp(self):
        # Create a mock cube mesh for testing
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
            [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
        ])
        faces = np.array([
            [0, 1, 2], [0, 2, 3], [0, 4, 7], [0, 7, 3],
            [4, 5, 6], [4, 6, 7], [5, 1, 2], [5, 2, 6],
            [2, 3, 6], [3, 7, 6], [0, 1, 5], [0, 5, 4]
        ])
        self.mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    def test_mesh_is_closed(self):
        self.assertTrue(self.mesh.is_watertight)

    def test_no_boundary_edges(self):
    # For a closed mesh, all edges should be shared by exactly two faces
        edge_face_count = np.bincount(self.mesh.edges_unique.flatten())
        
        # Print debug information
        print("Edge face counts:", edge_face_count)
        print("Unique edge face counts:", np.unique(edge_face_count))
        
        # Check that all edges are shared by at least two faces
        self.assertTrue(np.all(edge_face_count >= 2), 
                        "Some edges are not shared by at least two faces")
        
        # Check that we have the expected number of vertices for a cube
        self.assertEqual(len(edge_face_count), 8, 
                        f"Expected 8 vertices, but got {len(edge_face_count)}")

    def test_sharp_edges(self):
        angle_threshold = np.radians(45)
        face_adjacency_angles = self.mesh.face_adjacency_angles
        sharp_edges = self.mesh.face_adjacency_edges[face_adjacency_angles > angle_threshold]
        # For a cube, all 12 edges should be sharp
        self.assertEqual(len(sharp_edges), 12)

    def test_sharp_vertices(self):
        angle_threshold = np.radians(45)
        face_adjacency_angles = self.mesh.face_adjacency_angles
        sharp_edges = self.mesh.face_adjacency_edges[face_adjacency_angles > angle_threshold]
        sharp_vertices = np.unique(sharp_edges.flatten())
        # For a cube, all 8 vertices should be sharp
        self.assertEqual(len(sharp_vertices), 8)

    def test_face_adjacency_angles(self):
        # In a cube, face adjacency angles should be either 0 (coplanar faces) or pi/2 (perpendicular faces)
        expected_angles = np.array([0, np.pi/2])
        actual_angles = np.unique(np.round(self.mesh.face_adjacency_angles, decimals=5))
        np.testing.assert_array_almost_equal(actual_angles, expected_angles, decimal=5)

if __name__ == '__main__':
    unittest.main(verbosity=2)