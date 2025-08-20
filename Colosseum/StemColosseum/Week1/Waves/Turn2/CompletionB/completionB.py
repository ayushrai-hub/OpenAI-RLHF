import numpy as np
from numpy.random import rand
from scipy.optimize import minimize

# Define the trial wave function
def trial_wave_function(x, omega, theta):
    # Normalization ensures wave function is appropriately scaled
    return omega * np.sin(theta * x / L)

# Define the local energy function: E_local = H * ψ / ψ
def local_energy(x, omega, theta):
    psi = trial_wave_function(x, omega, theta)
    # Second derivative for kinetic term
    psi_sec_deriv = -((theta2) * psi) / (L2)
    kinetic = -0.5 * psi_sec_deriv / psi
    potential = 0  # V(x) = 0 inside the box
    return kinetic + potential

# Metropolis-Hastings sampling to draw samples from |psi(x)|^2
def metropolis_hastings_sampling(omega, theta, num_samples=10000, step_size=0.5):
    samples = np.zeros(num_samples)
    x = np.random.rand() * L
    psi_squared = trial_wave_function(x, omega, theta)2

    for i in range(num_samples):
        # Propose a new position using a uniform random step
        x_new = x + step_size * (rand() - 0.5)
        # Reflect if outside boundaries
        if x_new < 0:
            x_new = -x_new
        elif x_new > L:
            x_new = 2*L - x_new

        psi_squared_new = trial_wave_function(x_new, omega, theta)2

        # Metropolis acceptance
        if psi_squared_new / psi_squared > rand():
            x, psi_squared = x_new, psi_squared_new

        samples[i] = x
    return samples

# Monte Carlo integration using the sampled points
def monte_carlo_energy(params, num_samples=10000):
    omega, theta = params
    # Generate samples for x according to |psi(x)|^2
    x_samples = metropolis_hastings_sampling(omega, theta, num_samples)
    energies = np.array([local_energy(x, omega, theta) for x in x_samples])
    return np.mean(energies)

# Define parameters
L = 1.0  # Box length
initial_params = [1.0, np.pi]  # Initial guesses for omega and theta
num_samples = 50000  # Increase number of Monte Carlo samples for accuracy

# Minimize the energy by adjusting the parameters omega and theta
result = minimize(lambda params: monte_carlo_energy(params, num_samples), initial_params,
                  method='Nelder-Mead', tol=1e-5)

omega_optimal, theta_optimal = result.x
energy_optimal = monte_carlo_energy([omega_optimal, theta_optimal], num_samples)

print(f"Optimal omega: {omega_optimal}")
print(f"Optimal theta: {theta_optimal}")
print(f"Estimated ground state energy: {energy_optimal}")
