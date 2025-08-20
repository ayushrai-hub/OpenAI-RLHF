# Unit tests
import unittest
from original import create_sparse_interaction_matrix
class TestSparseInteractionMatrix(unittest.TestCase):
    
    def test_empty_interactions(self):
        matrix, users, items = create_sparse_interaction_matrix([])
        self.assertEqual(matrix.shape, (0, 0))
        self.assertEqual(users, 0)
        self.assertEqual(items, 0)
    
    def test_single_interaction(self):
        matrix, users, items = create_sparse_interaction_matrix([(0, 0)])
        self.assertEqual(matrix.shape, (1, 1))
        self.assertTrue(matrix[0, 0])
        self.assertEqual(users, 1)
        self.assertEqual(items, 1)
    
    def test_multiple_interactions(self):
        interactions = [(0, 1), (0, 2), (1, 2), (3, 4)]
        matrix, users, items = create_sparse_interaction_matrix(interactions)
        self.assertEqual(matrix.shape, (4, 5))
        for user, item in interactions:
            self.assertTrue(matrix[user, item])
        self.assertEqual(users, 4)
        self.assertEqual(items, 5)

    def test_sparse_matrix_properties(self):
        
        interactions = [(0, 10), (5, 15), (10, 20)]
        matrix, users, items = create_sparse_interaction_matrix(interactions)
        self.assertEqual(matrix.shape, (11, 21))
        self.assertEqual(matrix.nnz, 3)  # Number of non-zero elements
    
    def test_duplicate_interactions(self):
        interactions = [(0, 1), (0, 1), (1, 2), (1, 2)]
        matrix, users, items = create_sparse_interaction_matrix(interactions)
        self.assertEqual(matrix.shape, (2, 3))
        self.assertEqual(matrix.nnz, 2)  # Only unique interactions should be counted
    
    def test_zero_based_indexing(self):
        interactions = [(0, 0), (1, 1)]
        matrix, users, items = create_sparse_interaction_matrix(interactions)
        self.assertEqual(matrix.shape, (2, 2))
        self.assertTrue(matrix[0, 0])
        self.assertTrue(matrix[1, 1])
    
    def test_large_sparse_matrix(self):
        interactions = [(i, i) for i in range(1000)] + [(999, 9999)]
        matrix, users, items = create_sparse_interaction_matrix(interactions)
        self.assertEqual(matrix.shape, (1000, 10000))
        self.assertEqual(matrix.nnz, 1001)

if __name__ == '__main__':
    unittest.main(verbosity=2)