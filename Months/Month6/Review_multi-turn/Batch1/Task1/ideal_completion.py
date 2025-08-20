import numpy as np
from scipy.integrate import solve_ivp

# Constants for the Kerr black hole
M = 1.0  # Mass of the black hole
a = 0.5  # Spin parameter of the black hole, |a| <= M

def compute_r(x: float, y: float, z: float) -> float:
    """Computes the radial coordinate r in Kerr-Schild coordinates."""
    return np.sqrt((np.sqrt(x**2 + y**2 + z**2 - a**2)**2 + a**2 * z**2 / (x**2 + y**2 + z**2 - a**2)))

def H_func(r: float, z: float) -> float:
    """Computes the function H used in the Kerr-Schild metric."""
    return M * r**3 / (r**4 + a**2 * z**2)

def l_mu_func(r: float, x: float, y: float, z: float) -> np.ndarray:
    """Computes the null vector l_mu in Kerr-Schild coordinates."""
    sigma = r**2 + a**2
    return np.array([
        1,
        (r * x + a * y) / sigma,
        (r * y - a * x) / sigma,
        z / r
    ])

def g_mu_nu(x: float, y: float, z: float) -> np.ndarray:
    """Computes the Kerr-Schild metric g_mu_nu at position (x, y, z)."""
    r = compute_r(x, y, z)
    H = H_func(r, z)
    l = l_mu_func(r, x, y, z)
    eta = np.diag([-1, 1, 1, 1])
    return eta + 2 * H * np.outer(l, l)

def compute_inverse_metric(g: np.ndarray) -> np.ndarray:
    """Computes the inverse of the metric tensor g_mu_nu."""
    return np.linalg.inv(g)

def partial_derivatives(func: callable, x: float, y: float, z: float, h: float = 1e-5) -> dict:
    """Computes the partial derivatives of a function with respect to x, y, and z."""
    df_dx = (func(x + h, y, z) - func(x - h, y, z)) / (2 * h)
    df_dy = (func(x, y + h, z) - func(x, y - h, z)) / (2 * h)
    df_dz = (func(x, y, z + h) - func(x, y, z - h)) / (2 * h)
    return {'x': df_dx, 'y': df_dy, 'z': df_dz}

def compute_christoffel_symbols(x: float, y: float, z: float) -> np.ndarray:
    """Computes the Christoffel symbols at position (x, y, z)."""
    r = compute_r(x, y, z)
    H = H_func(r, z)
    l = l_mu_func(r, x, y, z)
    g = g_mu_nu(x, y, z)
    g_inv = compute_inverse_metric(g)
    
    Gamma = np.zeros((4, 4, 4))
    for mu in range(4):
        for nu in range(4):
            for sigma in range(4):
                sum_term = 0.0
                for alpha in range(4):
                    partial_g_nu_alpha = partial_derivatives(lambda xi, yi, zi: g_mu_nu(xi, yi, zi)[nu, alpha], x, y, z)
                    partial_g_sigma_alpha = partial_derivatives(lambda xi, yi, zi: g_mu_nu(xi, yi, zi)[sigma, alpha], x, y, z)
                    partial_g_nu_sigma = partial_derivatives(lambda xi, yi, zi: g_mu_nu(xi, yi, zi)[nu, sigma], x, y, z)
                    sum_term += g_inv[mu, alpha] * (partial_g_nu_alpha['x'] + partial_g_sigma_alpha['x'] - partial_g_nu_sigma['x'])
                Gamma[mu, nu, sigma] = 0.5 * sum_term
    return Gamma

def geodesic_equations(t: float, Y: list, M: float, a: float) -> list:
    """Defines the geodesic equations for the Kerr metric."""
    x, y, z, pt, px, py, pz = Y
    r = compute_r(x, y, z)
    g = g_mu_nu(x, y, z)
    g_inv = compute_inverse_metric(g)
    Gamma = compute_christoffel_symbols(x, y, z)

    # Contravariant momentum components
    p = np.array([pt, px, py, pz])

    # Compute derivatives of the coordinates
    dx_dt = g_inv[1, :] @ p
    dy_dt = g_inv[2, :] @ p
    dz_dt = g_inv[3, :] @ p
    dpt_dt = 0  # pt is conserved in stationary spacetimes

    # Compute derivatives of the momentum components
    dp = np.zeros(4)
    for mu in range(4):
        sum_term = 0.0
        for nu in range(4):
            for sigma in range(4):
                sum_term -= Gamma[mu, nu, sigma] * p[nu] * p[sigma]
        dp[mu] = sum_term

    return [dx_dt, dy_dt, dz_dt, dpt_dt, dp[1], dp[2], dp[3]]

def integrate_geodesic(x0: float, y0: float, z0: float, px0: float, py0: float, pz0: float, max_distance: float) -> solve_ivp:
    """Integrates the geodesic equations from initial conditions until stopping criteria are met."""

    def event_horizon(t, Y):
        x, y, z = Y[0], Y[1], Y[2]
        r = compute_r(x, y, z)
        horizon_radius = M + np.sqrt(M**2 - a**2)
        return r - horizon_radius

    event_horizon.terminal = True
    event_horizon.direction = -1  # Stop when approaching the horizon from outside

    def max_distance_event(t, Y):
        x, y, z = Y[0], Y[1], Y[2]
        distance = np.sqrt(x**2 + y**2 + z**2)
        return max_distance - distance

    max_distance_event.terminal = True
    max_distance_event.direction = -1  # Stop when the geodesic extends beyond the initial distance

    # Initial conditions
    x_init, y_init, z_init = x0, y0, z0
    pt_init = -1  # Assume initial energy parameter (can be scaled)
    initial_state = [x_init, y_init, z_init, pt_init, px0, py0, pz0]

    # Integrate the geodesic
    sol = solve_ivp(
        fun=lambda t, Y: geodesic_equations(t, Y, M, a),
        t_span=(0, 100),  # Integration limits; can be adjusted
        y0=initial_state,
        events=[event_horizon, max_distance_event],
        rtol=1e-6,
        atol=1e-9
    )

    return sol