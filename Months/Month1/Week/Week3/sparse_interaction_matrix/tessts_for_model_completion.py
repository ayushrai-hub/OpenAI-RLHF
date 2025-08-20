import unittest
import numpy as np
from scipy.sparse import lil_matrix
from test_model_completion import create_sparse_interaction_matrix  # Replace 'your_module' with the actual module name

class TestCreateSparseInteractionMatrix(unittest.TestCase):

    def test_empty_interactions(self):
        matrix, users, items = create_sparse_interaction_matrix([])
        self.assertEqual(matrix.shape, (0, 0))
        self.assertEqual(users, 0)
        self.assertEqual(items, 0)

    def test_single_interaction(self):
        interactions = [(0, 0)]
        matrix, users, items = create_sparse_interaction_matrix(interactions)
        self.assertEqual(matrix.shape, (1, 1))
        self.assertEqual(matrix[0, 0], True)
        self.assertEqual(users, 1)
        self.assertEqual(items, 1)

    def test_multiple_interactions(self):
        interactions = [(0, 1), (0, 2), (1, 2), (3, 4)]
        matrix, users, items = create_sparse_interaction_matrix(interactions)
        self.assertEqual(matrix.shape, (4, 5))
        self.assertTrue(np.array_equal(matrix.toarray(), np.array([
            [False, True, True, False, False],
            [False, False, True, False, False],
            [False, False, False, False, False],
            [False, False, False, False, True]
        ])))
        self.assertEqual(users, 4)
        self.assertEqual(items, 5)

    def test_sparse_interactions(self):
        interactions = [(0, 10), (5, 5), (10, 0)]
        matrix, users, items = create_sparse_interaction_matrix(interactions)
        self.assertEqual(matrix.shape, (11, 11))
        self.assertEqual(matrix[0, 10], True)
        self.assertEqual(matrix[5, 5], True)
        self.assertEqual(matrix[10, 0], True)
        self.assertEqual(users, 11)
        self.assertEqual(items, 11)

    def test_duplicate_interactions(self):
        interactions = [(0, 1), (0, 1), (1, 2), (1, 2)]
        matrix, users, items = create_sparse_interaction_matrix(interactions)
        self.assertEqual(matrix.shape, (2, 3))
        self.assertTrue(np.array_equal(matrix.toarray(), np.array([
            [False, True, False],
            [False, False, True]
        ])))
        self.assertEqual(users, 2)
        self.assertEqual(items, 3)

if __name__ == '__main__':
    unittest.main(verbosity=2)