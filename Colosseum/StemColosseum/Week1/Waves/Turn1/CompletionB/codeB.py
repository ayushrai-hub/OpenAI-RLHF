import numpy as np
from scipy.optimize import minimize

# Define the normalized trial wave function
def trial_wave_function(x, omega, theta):
    norm_factor = np.sqrt(2 / L)
    return norm_factor * omega * np.sin(theta * x / L)

# Define the local energy function (E_local = T + V)
def local_energy(x, omega, theta):
    psi = trial_wave_function(x, omega, theta)
    d2psi_dx2 = - (theta / L)  2 * psi
    kinetic = -0.5 * d2psi_dx2 / psi
    potential = potential_energy(x)
    return kinetic + potential

# Perform Monte Carlo sampling to calculate the energy expectation value
def monte_carlo_sampling(params, num_samples=100000):
    omega, theta = params
    samples = np.random.uniform(0, L, num_samples)
    
    # Evaluate the wave function and local energy at sampled points
    psi_vals = trial_wave_function(samples, omega, theta)
    local_energies = local_energy(samples, omega, theta)
    
    # Calculate weighted average of local energies
    weights = psi_vals  2
    energy_expectation = np.sum(weights * local_energies) / np.sum(weights)
    
    return energy_expectation

# Define parameters
L = 1.0  # Box length
initial_params = [1.0, np.pi + 0.1]  # Initial guesses
num_samples = 100000  # Increased number of samples

# Set random seed for reproducibility
np.random.seed(42)

# Minimize the energy by refining the parameters omega and theta with constraints
result = minimize(
    monte_carlo_sampling,
    initial_params,
    bounds=[(0.5, 2.0), (np.pi - 1.0, np.pi + 1.0)],  # Tight bounds around expected values
    options={'maxiter': 1000}
)

omega_optimal, theta_optimal = result.x
energy_optimal = monte_carlo_sampling([omega_optimal, theta_optimal])

print(f"Optimal omega: {omega_optimal}")
print(f"Optimal theta: {theta_optimal}")
print(f"Ground state energy: {energy_optimal}")
