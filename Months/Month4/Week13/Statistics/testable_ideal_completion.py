import numpy as np

def one_var_lasso(v: np.ndarray, z: np.ndarray, lambda_val: float) -> float:
    """
    Solve the one-variable Lasso problem:
        min_b (1/(2n)) * ||v - b * z||^2 + lambda * |b|
    
    Parameters:
    v (np.ndarray): Response vector.
    z (np.ndarray): Feature vector.
    lambda_val (float): Regularization parameter.
    
    Returns:
    float: The optimized coefficient b.
    """
    n = len(v)
    
    # Calculate the least squares estimate for b
    z_norm_squared = np.dot(z, z)
    b_hat = np.dot(v, z) / z_norm_squared
    
    # Calculate the shrinkage factor
    eta = (n * lambda_val) / z_norm_squared
    
    # Apply the soft-thresholding rule
    if abs(b_hat) > eta:
        b = np.sign(b_hat) * (abs(b_hat) - eta)
    else:
        b = 0.0
    
    return b
