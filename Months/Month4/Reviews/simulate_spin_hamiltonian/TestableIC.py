import numpy as np
import qutip as qt
import matplotlib.pyplot as plt

def simulate_spin_hamiltonian(N: int = 2, B: float = 4.5, phi_deg: float = 30) -> None:
    # Constants
    mu_B = 9.274009994e-24        # Bohr magneton in J/T
    hbar = 1.054571817e-34        # Reduced Planck's constant in J·s

    # Electron characteristics (values based on GaAs)
    g_e = -0.44                   # Electron g-factor

    # Calculate electron Zeeman splitting (angular frequency, rad/s)
    omega_e = abs(g_e) * mu_B * B / hbar

    # Conversion of omega_e to MHz for clarity
    omega_e_MHz = omega_e / (2 * np.pi * 1e6)
    print(f"Electron Zeeman frequency: {omega_e_MHz:.2f} MHz")

    # Convert phi_deg to radians for calculations
    phi = np.deg2rad(phi_deg)
    cos_phi = np.cos(phi)
    sin_phi = np.sin(phi)

    # Parameters for nuclear spins
    nuclear_species = {
        '75As': {
            'omega_i': 2 * np.pi * 32.49e6,
            'a_i': 2 * np.pi * 0.320e6
        },
        '69Ga': {
            'omega_i': 2 * np.pi * 45.99e6,
            'a_i': 2 * np.pi * 0.269e6
        },
        '71Ga': {
            'omega_i': 2 * np.pi * 58.41e6,
            'a_i': 2 * np.pi * 0.342e6
        }
    }

    # Electron spin operators (spin-1/2)
    Sx = qt.sigmax() / 2
    Sy = qt.sigmay() / 2
    Sz = qt.sigmaz() / 2
    I_e = qt.qeye(2)  # Identity operator for electron

    # Nuclear spin operators (spin-3/2)
    I_nuc = qt.qeye(4)
    Ix, Iy, Iz = qt.jmat(1.5)  # Spin-3/2 operators

    # Calculating the total dimension of the Hilbert space
    hilbert_space = [I_e] + [I_nuc for _ in range(N)]
    H_dim = np.prod([op.shape[0] for op in hilbert_space])
    print(f"Total Hilbert space dimension: {H_dim}")

    # Constructing the total electron spin operators for the system
    Sx_total = qt.tensor([Sx] + [I_nuc for _ in range(N)])
    Sy_total = qt.tensor([Sy] + [I_nuc for _ in range(N)])
    Sz_total = qt.tensor([Sz] + [I_nuc for _ in range(N)])

    # Building the Hamiltonian starting with the electron Zeeman term
    H = omega_e * (cos_phi * Sz_total + sin_phi * Sx_total)

    # Adding nuclear terms for each nuclear spin
    species_list = list(nuclear_species.keys())
    for i in range(N):
        species = species_list[i % len(species_list)]
        params = nuclear_species[species]
        omega_i = params['omega_i']
        a_i = params['a_i']

        # Constructing nuclear spin operators for the Hamiltonian
        ops_Iz = [I_e] + [I_nuc for _ in range(N)]
        ops_Iz[i+1] = Iz
        Iz_total = qt.tensor(ops_Iz)

        ops_Ix = [I_e] + [I_nuc for _ in range(N)]
        ops_Ix[i+1] = Ix
        Ix_total = qt.tensor(ops_Ix)

        ops_Iy = [I_e] + [I_nuc for _ in range(N)]
        ops_Iy[i+1] = Iy
        Iy_total = qt.tensor(ops_Iy)

        # Integrating nuclear Zeeman and hyperfine terms into the Hamiltonian
        H += omega_i * Iz_total
        H += a_i * (Sx_total * Ix_total + Sy_total * Iy_total + Sz_total * Iz_total)

    # Initial state configuration (electron spin-up, nuclei ground state)
    electron_up = qt.basis(2, 0)
    nuclei_ground = [qt.basis(4, 0) for _ in range(N)]
    initial_state = qt.tensor([electron_up] + nuclei_ground)

    # Time evolution parameters
    tlist = np.linspace(0, 1e-5, 500)  # Simulation time in seconds

    # Defining observables (expectation values of Sx, Sy, Sz)
    observables = [Sx_total, Sy_total, Sz_total]

    # Solving the Schrödinger equation for the system's time evolution
    result = qt.mesolve(H, initial_state, tlist, [], observables)

    # Extract the expectation values from the result
    Sx_exp = result.expect[0]
    Sy_exp = result.expect[1]
    Sz_exp = result.expect[2]

    # Plotting the expectation values of Sx, Sy, and Sz as functions of time
    plt.figure(figsize=(10, 6))
    plt.plot(tlist, Sx_exp, label=r'$\langle S_x \rangle$')
    plt.plot(tlist, Sy_exp, label=r'$\langle S_y \rangle$')
    plt.plot(tlist, Sz_exp, label=r'$\langle S_z \rangle$')
    plt.title("Time Evolution of Electron Spin Components")
    plt.xlabel("Time (s)")
    plt.ylabel("Expectation values")
    plt.legend()
    plt.grid(True)
    plt.show()
