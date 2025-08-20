import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

def integrate_gradient_field(dSdh, dSdT, h, T, boundary_value):
    """
    Reconstructs a scalar field S(h, T) from its gradients dSdh and dSdT using the Poisson equation.

    Parameters:
        dSdh (np.ndarray): Flattened array of partial derivatives ∂S/∂h.
        dSdT (np.ndarray): Flattened array of partial derivatives ∂S/∂T.
        h (np.ndarray): Flattened array of h-grid values.
        T (np.ndarray): Flattened array of T-grid values, includes boundary at T = 100.
        boundary_value (float or np.ndarray): Scalar field value S at the boundary T = 100. 
                                              Can be a scalar (uniform boundary value) or a flattened array matching the grid points.

    Returns:
        S_grid (np.ndarray): Reconstructed scalar field S reshaped into a 2D grid.
        H (np.ndarray): Reshaped 2D grid of h values.
        T_grid (np.ndarray): Reshaped 2D grid of T values.
    """
    h_unique = np.unique(h)
    T_unique = np.unique(T)
    Nh, NT = len(h_unique), len(T_unique)
    
    dh = np.diff(h_unique).mean()
    dT = np.diff(T_unique).mean()
    
    dSdh_grid = dSdh.reshape(NT, Nh)
    dSdT_grid = dSdT.reshape(NT, Nh)
    H, T_grid = np.meshgrid(h_unique, T_unique)
    
    d2Sdh2 = np.zeros_like(dSdh_grid)
    d2SdT2 = np.zeros_like(dSdT_grid)
    
    d2Sdh2[:, 1:-1] = (dSdh_grid[:, 2:] - dSdh_grid[:, :-2]) / (2 * dh)
    d2SdT2[1:-1, :] = (dSdT_grid[2:, :] - dSdT_grid[:-2, :]) / (2 * dT)
    
    rhs = d2Sdh2 + d2SdT2
    rhs_flat = rhs.flatten()
    
    N = Nh * NT
    data, rows, cols = [], [], []
    
    for idx in range(N):
        i, j = divmod(idx, Nh)
        
        if T_unique[i] == 100:
            data.append(1.0)
            rows.append(idx)
            cols.append(idx)
            if np.isscalar(boundary_value):
                rhs_flat[idx] = boundary_value
            else:
                rhs_flat[idx] = boundary_value[idx]
        elif i == 0 or i == NT - 1 or j == 0 or j == Nh - 1:
            data.append(1.0)
            rows.append(idx)
            cols.append(idx)
            rhs_flat[idx] = 0.0
        else:
            data.append(-2.0 / dh**2 -2.0 / dT**2)
            rows.append(idx)
            cols.append(idx)
            
            data.append(1.0 / dh**2)
            rows.append(idx)
            cols.append(idx + 1)
            
            data.append(1.0 / dh**2)
            rows.append(idx)
            cols.append(idx - 1)
            
            data.append(1.0 / dT**2)
            rows.append(idx)
            cols.append(idx + Nh)
            
            data.append(1.0 / dT**2)
            rows.append(idx)
            cols.append(idx - Nh)
    
    Laplacian = sp.coo_matrix((data, (rows, cols)), shape=(N, N)).tocsr()
    S_flat = spla.spsolve(Laplacian, rhs_flat)
    S_grid = S_flat.reshape(NT, Nh)
    
    return S_grid, H, T_grid
