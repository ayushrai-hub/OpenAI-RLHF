
import numpy as np
import scipy.sparse
import scipy.sparse.linalg
import matplotlib.pyplot as plt

def integrate_gradient_field(dSdh, dSdT, h, T, boundary_value):
    """
    Reconstruct S(h, T) from gradient data (dSdh, dSdT)
    via the Poisson equation ∇²S = ∂(dSdh)/∂h + ∂(dSdT)/∂T
    """
    # Extract unique h and T values and calculate differentials
    Nh, NT = len(np.unique(h)), len(np.unique(T))
    h_unique, T_unique = np.unique(h), np.unique(T)
    dh, dT = h_unique[1] - h_unique[0], T_unique[1] - T_unique[0]

    # Reshape data into two-dimensional arrays for processing
    H = h.reshape((NT, Nh))
    T_grid = T.reshape((NT, Nh))
    dSdh_grid = dSdh.reshape((NT, Nh))
    dSdT_grid = dSdT.reshape((NT, Nh))

    # Calculating divergence of the gradient field.
    divergence = np.zeros_like(dSdh_grid)
    divergence[:, 1:-1] = (dSdh_grid[:, 2:] - dSdh_grid[:, :-2]) / (2 * dh)
    divergence[:, 0] = (dSdh_grid[:, 1] - dSdh_grid[:, 0]) / dh
    divergence[:, -1] = (dSdh_grid[:, -1] - dSdh_grid[:, -2]) / dh
    divergence[1:-1, :] += (dSdT_grid[2:, :] - dSdT_grid[:-2, :]) / (2 * dT)
    divergence[0, :] += (dSdT_grid[1, :] - dSdT_grid[0, :]) / dT
    divergence[-1, :] += (dSdT_grid[-1, :] - dSdT_grid[-2, :]) / dT

    # Flatten the RHS for matrix-solving
    RHS_flat = divergence.flatten()

    # Constructing the laplacian operator using finite differences
    N = Nh * NT
    laplacian_diags, indices = [], []
    diagonal = -4 * np.ones(N)
    laplacian_diags.append(diagonal)
    indices.append(0)

    # Generating sparse matrix structure
    east = np.ones(N)
    east[np.arange(1, N) % Nh == 0] = 0 # Avoid wrap-around
    laplacian_diags.append(east)
    indices.append(1)

    west = np.ones(N)
    west[np.arange(N) % Nh == 0] = 0  # Zero for left boundary
    laplacian_diags.append(west)
    indices.append(-1)

    north = np.ones(N)
    north[:Nh] = 0  # No north boundary for the top row
    laplacian_diags.append(north)
    indices.append(-Nh)

    south = np.ones(N)
    south[-Nh:] = 0  # No south boundary for the bottom row
    laplacian_diags.append(south)
    indices.append(Nh)

    # Create a sparse matrix for the Laplacian operator
    Laplacian = scipy.sparse.diags(laplacian_diags, indices, shape=(N, N), format='csr')

    # Apply boundary condition at T = 100
    for i in range(N):
        row_index = i // Nh
        if T_grid[row_index, 0] == 100:  # Find the rows corresponding to T = 100
            Laplacian[i, :] = 0  # Zero out the row
            Laplacian[i, i] = 1  # Set diagonal to 1 to enforce boundary condition
            RHS_flat[i] = boundary_value  # Set RHS to boundary condition value

    # Solve the Poisson equation
    S_flat = scipy.sparse.linalg.spsolve(Laplacian, RHS_flat)

    # Reshape the result into a 2D array
    S_grid = S_flat.reshape((NT, Nh))

    return S_grid, H, T_grid
