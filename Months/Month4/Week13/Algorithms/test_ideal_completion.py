import unittest
import time
from testableIC import DijkstraComparison

class TestDijkstraAlgorithm(unittest.TestCase):
    def setUp(self):
        # It Initialize the DijkstraComparison instance for each test
        self.dijkstra = DijkstraComparison()
        
    def test_single_vertex_graph(self):
        # It tests both implementations with a single-vertex graph
        matrix = [[0]]
        adj_list = [[]]
        
        matrix_result = self.dijkstra.matrix_dijkstra(matrix, 0)
        list_result = self.dijkstra.list_dijkstra(adj_list, 0)
        
        self.assertEqual(matrix_result, [0])
        self.assertEqual(list_result, [0])
        
    def test_disconnected_graph(self):
        # It tests the graph with no edges between vertices
        matrix = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        adj_list = [[], [], []]
        
        matrix_result = self.dijkstra.matrix_dijkstra(matrix, 0)
        list_result = self.dijkstra.list_dijkstra(adj_list, 0)
        
        expected = [0, float('inf'), float('inf')]
        self.assertEqual(matrix_result, expected)
        self.assertEqual(list_result, expected)
        
    def test_simple_path(self):
        # It verifies that the basic shortest path calculation works correctly
        matrix = [
            [0, 1, 0],
            [1, 0, 2],
            [0, 2, 0]
        ]
        adj_list = [
            [(1, 1)],
            [(0, 1), (2, 2)],
            [(1, 2)]
        ]
        
        matrix_result = self.dijkstra.matrix_dijkstra(matrix, 0)
        list_result = self.dijkstra.list_dijkstra(adj_list, 0)
        
        expected = [0, 1, 3]
        self.assertEqual(matrix_result, expected)
        self.assertEqual(list_result, expected)
        
    def test_cyclic_graph(self):
        # It verifies that the algorithm finds shortest path even with cycles present in the vertices
        matrix = [
            [0, 1, 4],
            [1, 0, 2],
            [4, 2, 0]
        ]
        adj_list = [
            [(1, 1), (2, 4)],
            [(0, 1), (2, 2)],
            [(0, 4), (2, 2)]
        ]
        
        matrix_result = self.dijkstra.matrix_dijkstra(matrix, 0)
        list_result = self.dijkstra.list_dijkstra(adj_list, 0)
        
        expected = [0, 1, 3]
        self.assertEqual(matrix_result, expected)
        self.assertEqual(list_result, expected)
        
    def test_negative_edge_detection(self):
        # It tests the rejection of negative edge weights.
        matrix = [
            [0, -1],
            [-1, 0]
        ]
        adj_list = [
            [(1, -1)],
            [(0, -1)]
        ]
        
        with self.assertRaises(ValueError):
            self.dijkstra.matrix_dijkstra(matrix, 0)
        with self.assertRaises(ValueError):
            self.dijkstra.list_dijkstra(adj_list, 0)
            
    def test_identical_results(self):
        # It tests that both implementations give identical results for the same graph
        # Generate random graph with both representations
        V = 50
        matrix, adj_list = self.dijkstra.generate_graphs(V)
        
        matrix_result = self.dijkstra.matrix_dijkstra(matrix, 0)
        list_result = self.dijkstra.list_dijkstra(adj_list, 0)
        
        self.assertEqual(matrix_result, list_result)
        
    def test_performance_comparison(self):
        # It tests that list implementation is faster for large sparse graphs
        V = 500  # Large enough to see performance difference
        matrix, adj_list = self.dijkstra.generate_graphs(V)
        
        start = time.perf_counter()
        self.dijkstra.matrix_dijkstra(matrix, 0)
        matrix_time = time.perf_counter() - start
        
        start = time.perf_counter()
        self.dijkstra.list_dijkstra(adj_list, 0)
        list_time = time.perf_counter() - start
        
        self.assertLess(list_time, matrix_time)
        
    def test_graph_generation(self):
        # It verifies that graph generation produces valid input for both implementations
        V = 100
        matrix, adj_list = self.dijkstra.generate_graphs(V)
        
        # Test matrix properties
        self.assertEqual(len(matrix), V)
        self.assertTrue(all(len(row) == V for row in matrix))
        self.assertTrue(all(matrix[i][j] >= 0 for i in range(V) for j in range(V)))
        
        # Test adjacency list properties
        self.assertEqual(len(adj_list), V)
        self.assertTrue(all(all(0 <= v < V for v, _ in neighbors) for neighbors in adj_list))
        
    def test_empty_graph(self):
        # It tests edge cases of empty graph input
        matrix = []
        adj_list = []
        
        with self.assertRaises(ValueError):
            self.dijkstra.matrix_dijkstra(matrix, 0)
        with self.assertRaises(ValueError):
            self.dijkstra.list_dijkstra(adj_list, 0)
            
    def test_invalid_source(self):
        # It tests invalid source vertex indices
        matrix = [[0, 1], [1, 0]]
        adj_list = [[(1, 1)], [(0, 1)]]
        
        with self.assertRaises(ValueError):
            self.dijkstra.matrix_dijkstra(matrix, 2)
        with self.assertRaises(ValueError):
            self.dijkstra.list_dijkstra(adj_list, -1)

if __name__ == '__main__':
    unittest.main(verbosity=2)