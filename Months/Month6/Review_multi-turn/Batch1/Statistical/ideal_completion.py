import numpy as np

def one_var_lasso(v: np.ndarray, z: np.ndarray, lambda_val: float) -> float:
    if v.size == 0 or z.size == 0:
        raise ValueError("Input arrays v and z must not be empty.")
    if v.shape != z.shape:
        raise ValueError("Input arrays v and z must have the same shape.")
    if lambda_val < 0:
        raise ValueError("Regularization parameter lambda_val must be non-negative.")
    z_norm_squared = np.dot(z, z)
    if z_norm_squared == 0:
        raise ValueError("Input array z must not be a zero vector.")
    n = len(v)
    b_hat = np.dot(v, z) / z_norm_squared
    threshold = lambda_val * n / z_norm_squared
    if b_hat > threshold:
        return b_hat - threshold
    elif b_hat < -threshold:
        return b_hat + threshold
    else:
        return 0.0
