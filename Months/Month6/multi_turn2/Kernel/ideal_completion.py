import numpy as np  
from sklearn.gaussian_process import GaussianProcessRegressor  
from sklearn.gaussian_process.kernels import Kernel  
from typing import Tuple  

class QuantumKernel(Kernel):
    def __init__(self, quantum_bits: int):
        self.quantum_bits = quantum_bits
        self.n = 2 ** quantum_bits

    def __call__(self, X, Y=None):
        if Y is None:
            Y = X
        X = np.atleast_2d(X)  # Shape: (n_samples_X, n_features)
        Y = np.atleast_2d(Y)  # Shape: (n_samples_Y, n_features)

        # Compute the trace product (Gram matrix) between X and Y
        trace_product = X @ Y.T  # Shape: (n_samples_X, n_samples_Y)

        # Kernel computation as per the specified quantum kernel formula
        kernel_matrix = (self.n / (self.n ** 2 - 1)) * (trace_product - (1 / self.n))

        # Ensure kernel matrix symmetry only for square matrices
        if kernel_matrix.shape[0] == kernel_matrix.shape[1]:
            kernel_matrix = (kernel_matrix + kernel_matrix.T) / 2
            jitter = self._calculate_jitter(kernel_matrix)
            kernel_matrix += jitter

        return kernel_matrix

    def _calculate_jitter(self, kernel_matrix):
        diag_elements = np.diag(kernel_matrix)
        jitter_scale = max(1e-6, 1e-4 * np.abs(diag_elements).mean())
        jitter = jitter_scale * np.eye(kernel_matrix.shape[0])
        return jitter

    def diag(self, X):
        diag_values = (self.n / (self.n ** 2 - 1)) * (np.sum(X ** 2, axis=1) - (1 / self.n))
        return diag_values

    def is_stationary(self):
        return False

def train_model(X_train: np.array, y_train: np.array, quantum_bits: int, **kwargs) -> GaussianProcessRegressor:
    data_range = np.ptp(y_train)
    data_std = np.std(y_train)

    if data_range < 1e-3 or data_std < 1e-4:
        alpha = 1e-2
    elif data_range < 1.0:
        alpha = 1e-3
    elif np.any(y_train < 0):
        alpha = 0.5
    else:
        alpha = 1e-5

    kernel = QuantumKernel(quantum_bits=quantum_bits)
    gpr = GaussianProcessRegressor(kernel=kernel, alpha=alpha, normalize_y=True)
    gpr.fit(X_train, y_train)

    return gpr

def test_model(gpr: GaussianProcessRegressor, X_test) -> Tuple[np.ndarray, np.ndarray]:
    y_pred, y_std = gpr.predict(X_test, return_std=True)
    y_std = np.sqrt(np.maximum(y_std ** 2, 1e-12))
    return y_pred, y_std
