import numpy as np
import qutip as qt
import matplotlib.pyplot as plt

def simulate_spin_hamiltonian(N: int = 2, B: float = 4.5, phi_deg: float = 30):
    """
    Simulates the time evolution of an electron-nuclear spin system in a magnetic field.
    
    Parameters:
    N (int): Number of nuclear spins in the system.
    B (float): Magnetic field strength in Tesla.
    phi_deg (float): Tilt angle (in degrees) of the electron quantization axis relative to the magnetic field.
    """
    # Physical constants
    mu_B = 9.274009994e-24  # Bohr magneton in J/T
    hbar = 1.054571817e-34  # Reduced Planck's constant in J·s
    
    # Electron g-factor
    g_electron = -0.44

    # Electron Zeeman splitting frequency (Hz)
    omega_e = abs(g_electron) * mu_B * B / hbar / (2 * np.pi)  # Convert to Hz
    print(f"Electron Zeeman frequency: {omega_e * 1e-6:.2f} MHz")

    # Convert tilt angle to radians
    phi = np.deg2rad(phi_deg)
    cos_phi = np.cos(phi)
    sin_phi = np.sin(phi)

    # Nuclear species properties: Zeeman frequency (Hz) and hyperfine coupling (Hz)
    nuclei = {
        '75As': {
            'omega_i': 7.22e6 * B,  # Nuclear Zeeman frequency in Hz (MHz/T * T)
            'a_i': 0.320e6          # Hyperfine coupling constant in Hz
        },
        '69Ga': {
            'omega_i': 10.22e6 * B,
            'a_i': 0.269e6
        },
        '71Ga': {
            'omega_i': 12.98e6 * B,
            'a_i': 0.342e6
        }
    }

    # Electron spin operators (spin-1/2)
    Sx = qt.sigmax() / 2
    Sy = qt.sigmay() / 2
    Sz = qt.sigmaz() / 2

    # Nuclear spin operators (spin-3/2)
    Ix_single = qt.jmat(1.5, 'x')
    Iy_single = qt.jmat(1.5, 'y')
    Iz_single = qt.jmat(1.5, 'z')

    # Construct total spin operators via tensor products
    # Total Hilbert space: Electron (2) x N nuclei (4^N)
    op_list_Sx = [Sx] + [qt.qeye(4) for _ in range(N)]
    op_list_Sy = [Sy] + [qt.qeye(4) for _ in range(N)]
    op_list_Sz = [Sz] + [qt.qeye(4) for _ in range(N)]

    Sx_total = qt.tensor(op_list_Sx)
    Sy_total = qt.tensor(op_list_Sy)
    Sz_total = qt.tensor(op_list_Sz)

    # Initialize total Hamiltonian with electron Zeeman term
    H = omega_e * (cos_phi * Sz_total + sin_phi * Sx_total)

    # Loop over each nucleus to add nuclear Zeeman and hyperfine interaction terms
    nucleus_keys = list(nuclei.keys())
    for i in range(N):
        nucleus = nuclei[nucleus_keys[i % len(nucleus_keys)]]
        omega_i = nucleus['omega_i']
        a_i = nucleus['a_i']

        # Construct nuclear spin operators in total Hilbert space
        op_list_Ix = [qt.qeye(2)] + [qt.qeye(4) for _ in range(N)]
        op_list_Iy = [qt.qeye(2)] + [qt.qeye(4) for _ in range(N)]
        op_list_Iz = [qt.qeye(2)] + [qt.qeye(4) for _ in range(N)]

        # Replace the ith nuclear identity operator with the nuclear spin operator
        op_list_Ix[i + 1] = Ix_single
        op_list_Iy[i + 1] = Iy_single
        op_list_Iz[i + 1] = Iz_single

        Ix_total = qt.tensor(op_list_Ix)
        Iy_total = qt.tensor(op_list_Iy)
        Iz_total = qt.tensor(op_list_Iz)

        # Nuclear Zeeman term
        H += omega_i * Iz_total

        # Hyperfine interaction term
        H += a_i * (Sx_total * Ix_total + Sy_total * Iy_total + Sz_total * Iz_total)

    # Initial state: electron spin-up and each nucleus in its ground (lowest
    # Continuing the code from the previous block

    # Initial state: electron spin-up and each nucleus in its ground (lowest m) state
    electron_state = qt.basis(2, 0)  # Spin-up state |0>
    nuclear_ground_state = qt.basis(4, 3)  # Spin-3/2, m = -3/2 (lowest state)

    # Construct total initial state via tensor products
    initial_states = [electron_state] + [nuclear_ground_state for _ in range(N)]
    psi0 = qt.tensor(initial_states)

    # Time array for simulation (0 to 1 microsecond, 1000 points)
    t = np.linspace(0, 1e-6, 1000)

    # Observables: expectation values of electron spin components
    expect_ops = [Sx_total, Sy_total, Sz_total]

    # Time evolution of the system using QuTiP's mesolve
    result = qt.mesolve(H, psi0, t, [], expect_ops)

    # Extract expectation values from the result
    expect_x, expect_y, expect_z = result.expect

    # Plot the electron spin expectation values over time
    plt.figure(figsize=(10, 6))
    plt.plot(t * 1e6, expect_x, label='<Sx>')
    plt.plot(t * 1e6, expect_y, label='<Sy>')
    plt.plot(t * 1e6, expect_z, label='<Sz>')
    plt.xlabel('Time (μs)')
    plt.ylabel('Expectation value')
    plt.title('Electron Spin Expectation Values over Time')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    simulate_spin_hamiltonian(N=2, B=4.5, phi_deg=30)
