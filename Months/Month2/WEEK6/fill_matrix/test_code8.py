import numpy as np
from sklearn.mixture import GaussianMixture
import unittest

# Assuming the fill_matrix function is in a module named 'matrix_filler'
from original import fill_matrix

class TestFillMatrix(unittest.TestCase):

    def setUp(self):
        # Set up a simple mixture model for testing
        self.X = np.array([
            [1.0, 0.0, 3.0],
            [0.0, 2.0, 0.0],
            [4.0, 5.0, 6.0]
        ])
        self.means = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        self.covariances = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        self.weights = np.array([0.7, 0.3])
        
        self.gmm = GaussianMixture(n_components=2, covariance_type='diag')
        self.gmm.means_ = self.means
        self.gmm.covariances_ = self.covariances
        self.gmm.weights_ = self.weights

    def test_fill_matrix_shape(self):
        X_filled = fill_matrix(self.X, self.gmm)
        self.assertEqual(X_filled.shape, self.X.shape)

    def test_fill_matrix_observed_values_unchanged(self):
        X_filled = fill_matrix(self.X, self.gmm)
        np.testing.assert_array_almost_equal(X_filled[self.X != 0], self.X[self.X != 0])

    def test_fill_matrix_missing_values_filled(self):
        X_filled = fill_matrix(self.X, self.gmm)
        self.assertTrue(np.all(X_filled != 0))

    def test_fill_matrix_rounding(self):
        X_filled = fill_matrix(self.X, self.gmm, decimal_places=3)
        self.assertTrue(np.all(np.round(X_filled, 3) == X_filled))

    def test_fill_matrix_deterministic(self):
        X_filled1 = fill_matrix(self.X, self.gmm)
        X_filled2 = fill_matrix(self.X, self.gmm)
        np.testing.assert_array_almost_equal(X_filled1, X_filled2)

if __name__ == '__main__':
    unittest.main(verbosity=2)