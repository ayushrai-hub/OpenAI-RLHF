import numpy as np

# Define the GELU function
def gelu(x):
    return 0.5 * x * (1 + np.tanh(np.sqrt(2 / np.pi) * (x + 0.044715 * x**3)))

# Define the sigmoid function
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# Define the mixed activation function, renamed to improved_step_transition for testing
def improved_step_transition(x, beta=1.0):
    """
    Mixed activation function transitioning from GELU to a step function.

    Parameters:
    - x: Input values.
    - beta: Transition parameter from 0 to 1 (renamed from alpha to beta for clarity).
            beta=0: Pure GELU.
            beta=1: Resembles step function using sigmoid.
    
    Returns:
    - Resultant activated values.
    """
    # Set a minimum for beta to prevent division by zero
    beta = np.clip(beta, 1e-6, 1.0)

    # Calculate the temperature-dependent sigmoid
    return (1 - beta) * gelu(x) + beta * sigmoid(x / beta)
