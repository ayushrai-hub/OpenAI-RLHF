import numpy as np
from scipy.optimize import minimize

# Define the normalized trial wave function
def trial_wave_function(x, omega, theta):
    norm_factor = np.sqrt(2 / L)
    return norm_factor * omega * np.sin(theta * x / L)

# Define the box potential energy (V(x) = 0 inside the box)
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

# Perform Monte Carlo sampling to calculate the energy expectation value
def monte_carlo_sampling(params, num_samples=10000):
    omega, theta = params
    samples = np.random.uniform(0, L, num_samples)
    energies = np.array([local_energy(x, omega, theta) for x in samples])
    return np.mean(energies)

# Define parameters
L = 1.0  # Box length
initial_params = [1.0, 2.0]  # Better initial values for omega and theta
num_samples = 10000  # Higher number of Monte Carlo samples

# Minimize the energy by refining the parameters omega and theta with constraints
result = minimize(
    lambda params: monte_carlo_sampling(params),
    initial_params,
    bounds=[(0.5, 2.0), (np.pi, 2*np.pi)],  # Logical constraints for omega and theta
    options={'maxiter': 1000}
)

omega_optimal, theta_optimal = result.x
energy_optimal = monte_carlo_sampling([omega_optimal, theta_optimal])

print(f"Optimal omega: {omega_optimal}")
print(f"Optimal theta: {theta_optimal}")
print(f"Ground state energy: {energy_optimal}")
