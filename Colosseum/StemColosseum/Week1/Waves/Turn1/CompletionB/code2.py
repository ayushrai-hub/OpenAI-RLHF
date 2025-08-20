import numpy as np

# Define the trial wave function
def trial_wave_function(x, omega, theta):
    return omega * np.sin(theta * x / L)

# Define the potential energy for a particle in a box (V(x) = 0 inside the box)
def potential_energy(x):
    return 0 if 0 <= x <= L else np.inf

# Define the kinetic energy operator (-ħ²/2m * d²/dx²)
def kinetic_energy(x, omega, theta):
    wave_func = trial_wave_function(x, omega, theta)
    second_derivative = -theta**2 * wave_func / L**2
    return -0.5 * second_derivative

# Define the local energy function (E_local = T + V)
def local_energy(x, omega, theta):
    kinetic = kinetic_energy(x, omega, theta)
    potential = potential_energy(x)
    return kinetic + potential

# Perform Monte Carlo sampling to calculate the expectation value of the energy
def monte_carlo_sampling(params, num_samples=10000):
    omega, theta = params
    samples = np.random.uniform(0, L, num_samples)
    energies = np.array([local_energy(x, omega, theta) for x in samples])
    return np.mean(energies)

# Define the parameters
L = 1.0  # Length of the box
initial_params = [1.0, 1.0]  # Initial guesses for omega and theta
num_samples = 1000  # Number of Monte Carlo samples

# Minimize the energy by adjusting the variational parameters omega and theta
from scipy.optimize import minimize

result = minimize(lambda params: monte_carlo_sampling(params), initial_params)
omega_optimal, theta_optimal = result.x
energy_optimal = monte_carlo_sampling([omega_optimal, theta_optimal])

print(f"Optimal omega: {omega_optimal}")
print(f"Optimal theta: {theta_optimal}")
print(f"Ground state energy: {energy_optimal}")
