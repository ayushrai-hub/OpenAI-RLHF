# ideal_completion.py

import numpy as np

# True function f(x)
def f(x):
    return np.sin(2 * np.pi * x)

# Surrogate model 
def surrogate_model(x):
    random_noise = 0.1 * np.random.randn(*x.shape)
    return 0.8 * np.sin(2 * np.pi * x) + random_noise

# Weight function
def w(x):
    return np.exp(-x**2)  

# Monte Carlo Integration for IMSE_w
def monte_carlo_imse_w(domain, num_samples=1000):
    # Sample points from the domain
    x_samples = np.random.uniform(domain[0], domain[1], num_samples)
    
    # Compute the squared error between true function and surrogate model
    errors_squared = (f(x_samples) - surrogate_model(x_samples))**2
    
    # Apply the weight function
    weighted_errors = w(x_samples) * errors_squared
    
    # Approximate the IMSE using the average of the weighted errors
    imse_w = np.mean(weighted_errors)
    
    return imse_w