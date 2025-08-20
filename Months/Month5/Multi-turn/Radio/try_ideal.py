
import numpy as np
import matplotlib.pyplot as plt

class RadioInterferometerSimulation:
    def __init__(self, f=1.4e9, Db=1000, B=45, La=30, sigma_delta_t=1e-12, t_total=10, dt=0.001):
        self.c = 3e8  # Speed of light (m/s)
        self.f = f  # Observation frequency (Hz)
        self.lambda_ = self.c / self.f  # Wavelength (m)
        self.Db = Db  # Distance between antennas (meters)
        self.B = B  # Orientation from true north (degrees)
        self.La = La  # Latitude (degrees)
        self.sigma_delta_t = sigma_delta_t  # Timing error std dev (seconds)
        self.t_total = t_total  # Total observation time (seconds)
        self.dt = dt  # Time step (seconds)
        self.t = np.arange(0, self.t_total, self.dt)  # Time array

    def generate_timing_errors(self):
        delta_t1 = self.sigma_delta_t * np.random.randn(len(self.t))  # Antenna 1 timing errors
        delta_t2 = self.sigma_delta_t * np.random.randn(len(self.t))  # Antenna 2 timing errors
        return delta_t1, delta_t2

    def calculate_phase_errors(self, delta_t1, delta_t2):
        phi1 = 2 * np.pi * self.f * delta_t1  # Phase error for Antenna 1
        phi2 = 2 * np.pi * self.f * delta_t2  # Phase error for Antenna 2
        delta_phi = phi1 - phi2  # Differential phase error
        return phi1, phi2, delta_phi

    def simulate_signals(self, phi1, phi2):
        tau_g = 0  # Assume no geometric delay
        s1 = np.exp(-1j * (2 * np.pi * self.f * (self.t - tau_g) - phi1))  # Signal at Antenna 1
        s2 = np.exp(-1j * (2 * np.pi * self.f * self.t - phi2))  # Signal at Antenna 2
        return s1, s2

    def calculate_visibility(self, s1, s2):
        V12 = s1 * np.conj(s2)  # Complex visibility
        V12_avg = np.mean(V12)  # Time-averaged visibility
        amp_V12 = np.abs(V12_avg)  # Visibility amplitude
        phase_V12 = np.angle(V12_avg)  # Visibility phase
        return V12, amp_V12, phase_V12

    def visualize_phase_errors(self, delta_phi, V12):
        # Plot and save phase error and visibility phase graphs
        plt.figure(figsize=(12, 6))

        plt.subplot(2, 1, 1)
        plt.plot(self.t, delta_phi)
        plt.xlabel('Time (s)')
        plt.ylabel('Relative Phase Error (rad)')
        plt.title('Relative Phase Error Due to LO Timing Instability')

        plt.subplot(2, 1, 2)
        plt.plot(self.t, np.angle(V12))
        plt.xlabel('Time (s)')
        plt.ylabel('Visibility Phase (rad)')
        plt.title('Visibility Phase Over Time')

        plt.tight_layout()
        plt.savefig("phase_errors.png")
        plt.close()

    def synthesize_image(self, V12):
        # Calculate UV coordinates
        u = (self.Db / self.lambda_) * np.cos(np.deg2rad(self.B))
        v = (self.Db / self.lambda_) * np.sin(np.deg2rad(self.B))

        # Grid setup
        grid_size = 256
        image_grid = np.zeros((grid_size, grid_size), dtype=complex)

        # Map UV point to grid
        u_max = self.Db / self.lambda_
        v_max = self.Db / self.lambda_
        du = (2 * u_max) / grid_size
        dv = (2 * v_max) / grid_size

        u_index = int((u + u_max) / du)
        v_index = int((v + v_max) / dv)
        if 0 <= u_index < grid_size and 0 <= v_index < grid_size:
            image_grid[u_index, v_index] = np.mean(V12)

        # FFT for image synthesis
        synthesized_image = np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(image_grid)))
        synthesized_image = np.abs(synthesized_image)

        # Normalize and save the image
        plt.imshow(synthesized_image, cmap='inferno', extent=(-u_max, u_max, -v_max, v_max))
        plt.colorbar(label='Intensity')
        plt.title('Synthesized Image')
        plt.xlabel('u (wavelengths)')
        plt.ylabel('v (wavelengths)')
        plt.savefig("simulated_image.png")
        plt.close()