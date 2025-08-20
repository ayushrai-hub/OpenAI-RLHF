import numpy as np  
from sklearn.gaussian_process import GaussianProcessRegressor  
from sklearn.gaussian_process.kernels import Kernel  
from typing import Tuple

class QuantumKernel(Kernel):
    def __init__(self, quantum_bits: int):
        self.quantum_bits = quantum_bits
        self.n = 2 ** quantum_bits
        self.scaling_factor = self.n / (self.n ** 2 - 1)

    def __call__(self, X, Y=None):
        X = np.atleast_2d(X)
        Y = X if Y is None else np.atleast_2d(Y)

        sigma_X = self._construct_sigma_matrix(X)
        sigma_Y = self._construct_sigma_matrix(Y)

        trace_products = self._compute_trace_product(sigma_X, sigma_Y)
        kernel_matrix = self.scaling_factor * (trace_products - 1 / self.n)

        if X.shape[0] == Y.shape[0] and np.array_equal(X, Y):
            kernel_matrix += 1e-8 * np.eye(kernel_matrix.shape[0])
        return kernel_matrix

    def diag(self, X):
        X = np.atleast_2d(X)
        sigma_X = self._construct_sigma_matrix(X)
        trace_products = self._compute_trace_product(sigma_X, sigma_X)
        diag_values = self.scaling_factor * (np.diag(trace_products) - 1 / self.n) + 1e-8
        return diag_values

    def is_stationary(self):
        return False

    def _construct_sigma_matrix(self, X):
        num_samples, state_vector_length = X.shape
        dim = int(np.sqrt(state_vector_length))
        if dim ** 2 != state_vector_length:
            raise ValueError("Each input sample must have a length equal to a perfect square to form a square matrix.")

        matrices = X.reshape(num_samples, dim, dim)
        return matrices

    def _compute_trace_product(self, matrices_X, matrices_Y):
        num_samples_X = matrices_X.shape[0]
        num_samples_Y = matrices_Y.shape[0]

        flat_X = matrices_X.reshape(num_samples_X, -1)
        flat_Y = matrices_Y.reshape(num_samples_Y, -1)

        trace_products = np.dot(flat_X, flat_Y.T)
        return trace_products

def train_model(X_train: np.array, y_train: np.array, quantum_bits: int, alpha: float = 1e-8, **kwargs) -> GaussianProcessRegressor:
    kernel = QuantumKernel(quantum_bits=quantum_bits)
    gpr = GaussianProcessRegressor(kernel=kernel, alpha=alpha)
    gpr.fit(X_train, y_train)
    return gpr

def test_model(gpr: GaussianProcessRegressor, X_test) -> Tuple[np.ndarray, np.ndarray]:
    y_pred, y_std = gpr.predict(X_test, return_std=True)
    return y_pred, y_std
