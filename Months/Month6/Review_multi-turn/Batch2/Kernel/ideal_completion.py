import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Kernel

class MyCustomKernel(Kernel):
    def __init__(self, n):
        self.n = n

    def __call__(self, X, Y=None, eval_gradient=False):
        # Compute the kernel matrix using the given formula
        if Y is None:
            Y = X
        # Use inner product for "Tr[sigma_i sigma_j]" on X and Y
        inner = np.dot(X, Y.T)
        K = (self.n/(self.n**2 - 1.0)) * (inner - 1.0/self.n)
        if eval_gradient:
            return K, np.zeros((X.shape[0], Y.shape[0], 0))
        return K

    def diag(self, X):
        # Diagonal entries: apply formula with X and X
        inner = np.sum(X * X, axis=1)
        return (self.n/(self.n**2 - 1.0)) * (inner - 1.0/self.n)

    def is_stationary(self):
        return False

def train_model(X_train: np.array, y_train: np.array, quantum_bits: int, **kwargs):
    n = 2 ** quantum_bits
    kernel = MyCustomKernel(n=n)
    alpha = kwargs.get('alpha', 1e-10)
    gpr = GaussianProcessRegressor(kernel=kernel, alpha=alpha)
    gpr.fit(X_train, y_train)
    return gpr

def test_model(gpr: GaussianProcessRegressor, X_test):
    return gpr.predict(X_test, return_std=True)
