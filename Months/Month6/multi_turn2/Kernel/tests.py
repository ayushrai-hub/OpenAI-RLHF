from ideal_completion import train_model, test_model
import unittest
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor


class TestGaussianRegressor(unittest.TestCase):
    def test_train_model_data_values_greater_than_one(self):
        # Test if the model is trained correctly when the samples have values greater than 1
        # This is an important test case because it verifies the correctness of the train functionality
        n_samples = 10
        quantum_bits = 2
        n = 2 ** quantum_bits  # For 2 quantum bits, n = 4

        X_train = np.array([np.random.uniform(high=2, low=1, size=n * n).flatten() for _ in range(n_samples)])
        y_train = np.random.rand(n_samples)  # Target outcome
        self.assertIsInstance(train_model(X_train, y_train, quantum_bits, alpha=0.5), GaussianProcessRegressor)

    def test_train_model_data_values_less_than_one(self):
        # Test if the model is trained correctly when the samples have values greater than 0 and less than 1
        # This is an important test case because it verifies the correctness of the train functionality
        n_samples = 10
        quantum_bits = 2
        n = 2 ** quantum_bits  # For 2 quantum bits, n = 4

        X_train = np.array([np.random.uniform(high=0.2, low=0, size=n * n).flatten() for _ in range(n_samples)])
        y_train = np.random.rand(n_samples)  # Target outcome
        self.assertIsInstance(train_model(X_train, y_train, quantum_bits, alpha=0.5),GaussianProcessRegressor)

    def test_train_model_data_values_negative(self):
        # Test if the model is trained correctly when the samples have values less than 0
        # This is an important test case because it verifies the correctness of the train functionality
        n_samples = 10
        quantum_bits = 2
        n = 2 ** quantum_bits  # For 2 quantum bits, n = 4

        X_train = np.array([np.random.uniform(high=-0.1, low=-0.09, size=n * n).flatten() for _ in range(n_samples)])
        y_train = np.random.rand(n_samples)  # Target outcome
        self.assertIsInstance(train_model(X_train, y_train, quantum_bits, alpha=0.5), GaussianProcessRegressor)

    def test_test_model_data_values_greater_than_one(self):
        # Test if the gpr model predicts correctly when samples have values greater than 1
        # This is an important test case because it verifies the correctness of the predict functionality
        n_samples = 10
        quantum_bits = 2
        np.random.seed(0)
        n = 2 ** quantum_bits  # For 2 quantum bits, n = 4
        X_train = np.array([np.random.uniform(high=2, low=1, size=n * n).flatten() for _ in range(n_samples)])
        y_train = np.random.rand(n_samples)  # Target outcome
        gpr = train_model(X_train, y_train, quantum_bits)
        X_test = np.array([np.random.uniform(high=2, low=1, size=n * n).flatten() for _ in range(5)])
        y_pred, y_std = test_model(gpr, X_test)
        np.testing.assert_allclose([0.30617674212589224, 0.590230658731861, 0.5379702867356707,
                                    0.6736445285648464, 0.8934783232240835], y_pred)

    def test_test_model_data_values_less_than_one(self):
        # Test if the gpr model predicts correctly when samples have values greater than 0 and less than 1
        # This is an important test case because it verifies the correctness of the predict functionality
        n_samples = 10
        quantum_bits = 2
        np.random.seed(0)
        n = 2 ** quantum_bits  # For 2 quantum bits, n = 4
        X_train = np.array([np.random.uniform(high=2, low=1, size=n * n).flatten() for _ in range(n_samples)])
        y_train = np.random.rand(n_samples)  # Target outcome
        gpr = train_model(X_train, y_train, quantum_bits)
        X_test = np.array([np.random.uniform(high=0.1, low=0, size=n * n).flatten() for _ in range(5)])
        y_pred, y_std = test_model(gpr, X_test)
        np.testing.assert_allclose([-0.03913925937623394, -0.010733867715637224,
                          -0.015959904915255216, -0.002392480732337432, 0.01959089873358466], list(y_pred))

    def test_test_model_data_values_negative(self):
        # Test if the gpr model predicts correctly when samples have negative values
        # This is an important test case because it verifies the correctness of the predict functionality
        n_samples = 10
        quantum_bits = 2
        np.random.seed(0)
        n = 2 ** quantum_bits  # For 2 quantum bits, n = 4
        X_train = np.array([np.random.uniform(high=2, low=1, size=n * n).flatten() for _ in range(n_samples)])
        y_train = np.random.rand(n_samples)  # Target outcome
        gpr = train_model(X_train, y_train, quantum_bits)
        X_test = np.array([np.random.uniform(high=-0.01, low=-0.1, size=n * n).flatten() for _ in range(5)])
        y_pred, y_std = test_model(gpr, X_test)
        np.testing.assert_allclose([-0.08421353014125911, -0.058648677646722255, -0.0633521111263783,
                                    -0.051141429361752214, -0.0313563878424224], y_pred)


if __name__ == '__main__':
    unittest.main(verbosity=2)