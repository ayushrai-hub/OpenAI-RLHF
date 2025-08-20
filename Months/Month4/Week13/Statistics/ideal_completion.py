
# ideal_completion.py
import numpy as np

def one_var_lasso(v, z, lambda_val):
    """
    Solves one-variable Lasso optimization: min_b (1/2n)||v - bz||^2 + λ|b|
    
    Parameters
    ----------
    v : array-like
        Response vector v = (v₁, ..., vₙ)ᵀ
    z : array-like
        Feature vector z = (z₁, ..., zₙ)ᵀ
    lambda_val : float
        Regularization parameter λ > 0
        
    Returns
    -------
    float
        Optimal coefficient b*
        
    Raises
    ------
    ValueError
        If inputs are empty, of different lengths, or if lambda is negative
    """
    # Input validation
    if lambda_val < 0:
        raise ValueError("lambda must be non-negative")
        
    # Convert inputs to numpy arrays
    v = np.asarray(v)
    z = np.asarray(z)
    
    # Check for empty arrays
    if v.size == 0 or z.size == 0:
        raise ValueError("Input arrays cannot be empty")
        
    # Check for matching lengths
    if v.size != z.size:
        raise ValueError("Input vectors must have the same length")
    
    n = len(v)
    
    # Calculate v^T z and ||z||^2
    vt_z = np.dot(v, z)
    z_norm_sq = np.dot(z, z)
    
    # Check for zero norm
    if z_norm_sq == 0:
        raise ValueError("Feature vector z cannot be zero")
    
    # OLS estimate: b̂ = (v^T z) / ||z||^2
    b_hat = vt_z / z_norm_sq
    
    # Soft thresholding parameter: η = 2nλ/||z||^2
    eta = (2 * n * lambda_val) / z_norm_sq
    
    # Apply soft thresholding operator:
    # b* = sign(b̂)(|b̂| - η/2)₊
    if abs(vt_z) > n * lambda_val:
        return (vt_z - np.sign(vt_z) * n * lambda_val) / z_norm_sq
    return 0.0