import numpy as np
import matplotlib.pyplot as plt

# Constants
mu_a = 10.0  # absorption coefficient in cm^-1
mu_s = 0.0   # scattering coefficient in cm^-1
L = 1.0      # thickness of the medium in cm
delta_z = 0.025  # depth interval for collecting data in cm
num_photons = 10000
num_sets = 5

def simulate_photon_attenuation(mu_a: float, mu_s: float, L: float, delta_z: float, num_photons: int, num_sets: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z_bins = np.arange(0, L + delta_z, delta_z)
    z_midpoints = z_bins[:-1] + delta_z / 2
    absorbed_counts = np.zeros_like(z_midpoints)
    
    for _ in range(num_sets):
        for _ in range(num_photons):
            z = 0
            while z < L:
                if mu_a == 0:
                    step = L - z
                else:
                    step = -np.log(np.random.rand()) / mu_a
                if z + step >= L:
                    break
                z += step
                bin_index = int(z / delta_z)
                if bin_index < len(absorbed_counts):
                    absorbed_counts[bin_index] += 1
                break

    total_photons = num_photons * num_sets
    fraction_absorbed = absorbed_counts / total_photons

    theoretical_fraction = np.exp(-mu_a * z_midpoints) * (1 - np.exp(-mu_a * delta_z))

    return z_midpoints, fraction_absorbed, theoretical_fraction

def plot_results(z_midpoints: np.ndarray, fraction_absorbed: np.ndarray, theoretical_fraction: np.ndarray, delta_z: float) -> None:
    plt.figure(figsize=(10, 6))
    plt.bar(z_midpoints, fraction_absorbed, width=delta_z, alpha=0.6, label='Monte Carlo Simulation')
    plt.plot(z_midpoints, theoretical_fraction, 'r-', label='Beer-Lambert Law')
    plt.xlabel('Depth (cm)')
    plt.ylabel('Fraction of Photons Absorbed')
    plt.title('Photon Absorption vs. Depth')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    z_midpoints, fraction_absorbed, theoretical_fraction = simulate_photon_attenuation(mu_a, mu_s, L, delta_z, num_photons, num_sets)
    plot_results(z_midpoints, fraction_absorbed, theoretical_fraction, delta_z)
