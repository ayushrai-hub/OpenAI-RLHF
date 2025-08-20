import numpy as np

# Define trial wave function
def trial_wave_function(x, beta):
    return np.sqrt(2 / L) * np.sin(np.pi * x / L)

# Define potential energy function for a box potential (V(x) = 0 within the box)
def potential_energy(x):
    return 0 if 0 <= x <= L else np.inf

# Define the kinetic energy operator (-ħ²/2m * d²/dx²)
def kinetic_energy(x, beta):
    psi = trial_wave_function(x, beta)
    second_derivative = -np.pi**2 * psi / L**2
    return -0.5 * second_derivative

# Define the local energy function (E_local = T + V)
def local_energy(x, beta):
    kinetic = kinetic_energy(x, beta)
    potential = potential_energy(x)
    return kinetic + potential

# Perform Monte Carlo sampling to determine energy expectation value
def monte_carlo_sampling(beta, num_samples=10000):
    samples = np.random.uniform(0, L, num_samples)
    energies = np.array([local_energy(x, beta) for x in samples])
    return np.mean(energies)

# Define parameters
L = 1.0  # Box length
beta_initial = 1.0  # Initial guess for variational parameter
num_samples = 10000  # Monte Carlo sample size

# Minimize energy by modifying the variational parameter beta
from scipy.optimize import minimize

result = minimize(lambda beta: monte_carlo_sampling(beta), beta_initial)
beta_optimal = result.x[0]
energy_optimal = monte_carlo_sampling(beta_optimal)

print(f"Optimal beta: {beta_optimal}")
print(f"Ground state energy: {energy_optimal}")
