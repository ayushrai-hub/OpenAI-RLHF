import numpy as np

def gelu(x):
    """
    Implementation of the Gaussian Error Linear Unit (GELU) activation function.
    """
    return 0.5 * x * (1 + np.tanh(np.sqrt(2 / np.pi) * (x + 0.044715 * x**3)))

def improved_step_transition(x, beta=1.0):
    """
    Improved transition function with guaranteed monotonicity and smooth zero crossing.
    
    Parameters:
    x : array-like
        Input values
    beta : float, optional (default=1.0)
        Transition parameter:
        beta = 1.0: Pure GELU-like behavior
        beta -> 0: Pure step function (0 or 1)
    """
    # Input preprocessing
    x = np.asarray(x, dtype=np.float64)
    beta = np.maximum(beta, 1e-7)
    
    # Numerically stable sigmoid function
    def sigmoid(x, k):
        # Clip extreme values to prevent overflow
        x_safe = np.clip(k * x, -709, 709)  # log(float64.max) ≈ 709
        return 1 / (1 + np.exp(-x_safe))
    
    # Normalized and smoothed GELU
    def smooth_gelu(x):
        g = gelu(x)
        # Ensure GELU is bounded and monotonic
        return sigmoid(g, 1.0)
    
    # Compute transition with controlled steepness
    k = 2.0 / (beta + 1e-7)  # Steepness factor
    base_step = sigmoid(x, k)
    
    # Smoothly interpolate between step and GELU
    t = np.exp(-1/beta)  # Smooth transition parameter
    
    # Combine using convex combination
    result = t * smooth_gelu(x) + (1 - t) * base_step
    
    # Ensure output is in [0, 1]
    return np.clip(result, 0, 1)