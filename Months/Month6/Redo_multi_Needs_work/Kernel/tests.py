from ideal_completion import train_model, test_model
import unittest
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
import warnings


class TestGaussianRegressor(unittest.TestCase):
    def setUp(self):
        # Suppress the specific warning about negative variances
        warnings.filterwarnings('ignore', message='Predicted variances smaller than 0.')
        np.random.seed(0)  # Ensure reproducibility across all tests
        
    def test_train_model_data_values_greater_than_one(self):
        # Test if the model is trained correctly when the samples have values greater than 1
        # This is an important test case because it verifies the correctness of the train functionality
        n_samples = 10
        quantum_bits = 2
        n = 2 ** quantum_bits

        X_train = np.array([np.random.uniform(high=2, low=1, size=n * n).flatten() for _ in range(n_samples)])
        y_train = np.random.rand(n_samples)
        self.assertIsInstance(train_model(X_train, y_train, quantum_bits, alpha=0.5), GaussianProcessRegressor)

    def test_train_model_data_values_less_than_one(self):
        # Test if the model is trained correctly when the samples have values greater than 0 and less than 1
        # This is an important test case because it verifies the correctness of the train functionality
        n_samples = 10
        quantum_bits = 2
        n = 2 ** quantum_bits

        X_train = np.array([np.random.uniform(high=0.2, low=0, size=n * n).flatten() for _ in range(n_samples)])
        y_train = np.random.rand(n_samples)
        self.assertIsInstance(train_model(X_train, y_train, quantum_bits, alpha=0.5), GaussianProcessRegressor)

    def test_train_model_data_values_negative(self):
        # Test if the model is trained correctly when the samples have values less than 0
        # This is an important test case because it verifies the correctness of the train functionality
        n_samples = 10
        quantum_bits = 2
        n = 2 ** quantum_bits

        X_train = np.array([np.random.uniform(high=-0.1, low=-0.09, size=n * n).flatten() for _ in range(n_samples)])
        y_train = np.random.rand(n_samples)
        self.assertIsInstance(train_model(X_train, y_train, quantum_bits, alpha=0.5), GaussianProcessRegressor)

    def test_test_model_data_values_greater_than_one(self):
        # Test if the gpr model predicts correctly when samples have values greater than 1
        # This is an important test case because it verifies the correctness of the predict functionality       
        n_samples = 10
        quantum_bits = 2
        n = 2 ** quantum_bits
        
        X_train = np.array([np.random.uniform(high=2, low=1, size=n * n).flatten() for _ in range(n_samples)])
        y_train = np.random.rand(n_samples)
        gpr = train_model(X_train, y_train, quantum_bits)
        X_test = np.array([np.random.uniform(high=2, low=1, size=n * n).flatten() for _ in range(5)])
        y_pred, y_std = test_model(gpr, X_test)
        
        expected = np.array([0.30617674, 0.59023066, 0.53797029, 0.67364453, 0.89347832])
        np.testing.assert_allclose(y_pred, expected, rtol=1e-6)

    def test_test_model_data_values_less_than_one(self):
        # Test if the gpr model predicts correctly when samples have values greater than 0 and less than 1
        # This is an important test case because it verifies the correctness of the predict functionality
        n_samples = 10
        quantum_bits = 2
        n = 2 ** quantum_bits
        
        X_train = np.array([np.random.uniform(high=2, low=1, size=n * n).flatten() for _ in range(n_samples)])
        y_train = np.random.rand(n_samples)
        gpr = train_model(X_train, y_train, quantum_bits)
        X_test = np.array([np.random.uniform(high=0.1, low=0, size=n * n).flatten() for _ in range(5)])
        y_pred, y_std = test_model(gpr, X_test)
        
        expected = np.array([-0.03913926, -0.01073387, -0.01595990, -0.00239248, 0.01959090])
        np.testing.assert_allclose(y_pred, expected, rtol=1e-6)

    def test_test_model_data_values_negative(self):
        # Test if the gpr model predicts correctly when samples have negative values
        # This is an important test case because it verifies the correctness of the predict functionality
        n_samples = 10
        quantum_bits = 2
        n = 2 ** quantum_bits
        
        X_train = np.array([np.random.uniform(high=2, low=1, size=n * n).flatten() for _ in range(n_samples)])
        y_train = np.random.rand(n_samples)
        gpr = train_model(X_train, y_train, quantum_bits)
        X_test = np.array([np.random.uniform(high=-0.01, low=-0.1, size=n * n).flatten() for _ in range(5)])
        y_pred, y_std = test_model(gpr, X_test)
        
        expected = np.array([-0.08421353, -0.05864868, -0.06335211, -0.05114143, -0.03135639])
        np.testing.assert_allclose(y_pred, expected, rtol=1e-6)


if __name__ == '__main__':
    unittest.main(verbosity=2)