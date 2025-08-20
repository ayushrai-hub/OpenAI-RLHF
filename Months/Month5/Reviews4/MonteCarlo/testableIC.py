import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor

# Gaussian Process or model predicting mean and variance
def surrogate_model(x, model):
    _, variance = model.predict(x, return_std=True)
    return variance**2  # Squared variance (MSE at x)

# Weighting function w(x)
def w(x):
    return 1.0  # Example: Uniform weight

# Monte Carlo integration of IMSE using weighting function
def monte_carlo_imse_w(model, domain, n_samples=1000):
    # Draw uniform samples inside the domain
    x_samples = np.random.uniform(domain[0], domain[1], n_samples)
    
    # Compute variance and weight at each sample spot
    imse_estimate = 0.0
    for x in x_samples:
        var_x = surrogate_model(np.array([x]), model)  # Retrieve variance using model
        weight_x = w(np.array([x]))  # Apply weight
        imse_estimate += weight_x * var_x
    
    # Monte Carlo evaluation of the integral
    imse_estimate /= n_samples
    return imse_estimate

# Example of the true function (optional if needed in your tests)
def f(x):
    return np.sin(x)

# Example using a Gaussian Process model
gp_model = GaussianProcessRegressor()
# Assume the GP has been previously trained with data

# Define the domain over which to compute IMSE
domain = [0, 10]  # Example domain [a, b]

# Calculate the IMSE using Monte Carlo integration
imse_value = monte_carlo_imse_w(gp_model, domain, n_samples=10000)
print(f"Estimated IMSE: {imse_value}")
