import numpy as np
import matplotlib.pyplot as plt

# Constants
c = 3e8  # Speed of light (m/s)

# Observational specifics
f = 1.4e9  # Frequency of observation (Hz)
lambda_ = c / f  # Wavelength (m)

# Antenna setup
Db = 1000  # Distance between antennas (meters)
B = 45  # Orientation from true north (degrees)
La = 30  # Geographical latitude of the setup (degrees)

# Timing instability specifics
sigma_delta_t = 1e-12  # LO timing error standard deviation (seconds)

# Simulation settings
t_total = 10  # Total duration of observation (seconds)
dt = 0.001  # Simulation time step (seconds)
t = np.arange(0, t_total, dt)  # Time array

# Random timing errors for each antenna
delta_t1 = sigma_delta_t * np.random.randn(len(t))  # Error for Antenna 1
delta_t2 = sigma_delta_t * np.random.randn(len(t))  # Error for Antenna 2

# Resulting phase errors
phi1 = 2 * np.pi * f * delta_t1  # Phase error for Antenna 1
phi2 = 2 * np.pi * f * delta_t2  # Phase error for Antenna 2
delta_phi = phi1 - phi2  # Differential phase error

# Zero geometric delay for a zenith source
tau_g = 0

# Simulated signals at the antennas
s1 = np.exp(-1j * (2 * np.pi * f * (t - tau_g) - phi1))
s2 = np.exp(-1j * (2 * np.pi * f * t - phi2))

# Visibility computation
V12 = s1 * np.conj(s2)

# Averaging over time for visibility
V12_avg = np.mean(V12)
# Extraction of amplitude and phase
amp_V12 = np.abs(V12_avg)
phase_V12 = np.angle(V12_avg)

# Display computed values
print(f'Visibility Amplitude: {amp_V12}')
print(f'Visibility Phase (radians): {phase_V12}')
# Error and visibility phase graphs
plt.figure(figsize=(12, 6))

plt.subplot(2, 1, 1)
plt.plot(t, delta_phi)
plt.xlabel('Time (s)')
plt.ylabel('Relative Phase Error (rad)')
plt.title('Relative Phase Error Due to LO Timing Instability')

plt.subplot(2, 1, 2)
plt.plot(t, np.angle(V12))
plt.xlabel('Time (s)')
plt.ylabel('Visibility Phase (rad)')
plt.title('Visibility Phase Over Time')

plt.tight_layout()
plt.show()

# UV plane coordinates
u = (Db / lambda_) * np.cos(np.deg2rad(B))
v = (Db / lambda_) * np.sin(np.deg2rad(B))

# Grid creation for UV coverage
uv_points = np.array([[u, v]])

# Visibility grid for image synthesis
V = V12  # Using single-baseline visibility for simplicity

# Basic gridding of visibilities
grid_size = 256  # Image grid size
image_grid = np.zeros((grid_size, grid_size), dtype=complex)

# Grid coordinate mapping
u_max = np.max(np.abs(u))
v_max = np.max(np.abs(v))
du = (2 * u_max) / grid_size
dv = (2 *