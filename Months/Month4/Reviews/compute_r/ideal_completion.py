# ideal_completion.py
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Constants
M = 1.0  # Black hole mass
a = 0.5  # Spin parameter (|a| < M)
epsilon = 1e-6  # Near to "just outside" the horizon

def compute_r(x, y, z):
    """
    Computes radial coordinate r from x, y, z coordinates in Kerr-Schild form.
    """
    rho2 = x**2 + y**2 + z**2
    B = a**2 - rho2
    C = -a**2 * z**2
    discriminant = B**2 - 4 * C
    if discriminant < 0:
        raise ValueError("Negative discriminant, not solvable for r^2")
    s1 = (-B + np.sqrt(discriminant)) / 2
    s2 = (-B - np.sqrt(discriminant)) / 2
    if s1 >= 0:
        r = np.sqrt(s1)
    elif s2 >= 0:
        r = np.sqrt(s2)
    else:
        raise ValueError("Negative solutions for r^2 not acceptable")
    return r

def H_func(r, z):
    """
    Calculates H(r, z) used in the Kerr-Schild metric.
    """
    numerator = M * r**3
    denominator = r**4 + a**2 * z**2
    return numerator / denominator

def l_mu_func(r, x, y, z):
    """
    Computes l_mu components in Kerr-Schild coordinates.
    """
    denom = r**2 + a**2
    l_t = 1.0
    l_x = (r * x + a * y) / denom
    l_y = (r * y - a * x) / denom
    l_z = z / r
    return np.array([l_t, l_x, l_y, l_z])

def g_mu_nu(x, y, z):
    """
    Computes the Kerr-Schild metric tensor g_mu_nu at (x, y, z).
    """
    r = compute_r(x, y, z)
    H = H_func(r, z)
    l_mu = l_mu_func(r, x, y, z)
    eta = np.array([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])  # Minkowski with (-, +, +, +)
    g = eta + 2 * H * np.outer(l_mu, l_mu)
    return g

def compute_inverse_metric(g):
    """
    Computes the inverse of the metric tensor.
    """
    return np.linalg.inv(g)

def partial_derivatives(func, x, y, z, h=1e-5):
    """
    Calculates numerical partial derivatives of a function func at (x, y, z).
    """
    partials = {}
    f0 = func(x, y, z)
    for var, val in zip(['x', 'y', 'z'], [x, y, z]):
        delta = np.zeros(3)
        offset = h if var == 'x' else h if var == 'y' else h
        delta = np.array([h if var == letter else 0.0 for letter in ['x', 'y', 'z']])
        f_plus = func(x + delta[0], y + delta[1], z + delta[2])
        partials[var] = (f_plus - f0) / h
    return partials

def compute_christoffel_symbols(x, y, z):
    """
    Computes Christoffel symbols Γ^lambda_mu_nu in Kerr-Schild coordinates.
    """
    g = g_mu_nu(x, y, z)
    g_inv = compute_inverse_metric(g)
    partials = {}
    for mu in range(4):
        for nu in range(4):
            func = lambda x, y, z: g_mu_nu(x, y, z)[mu, nu]
            partials_mu_nu = partial_derivatives(func, x, y, z)
            for var in ['x', 'y', 'z']:
                key = (mu, nu, var)
                partials[key] = partials_mu_nu[var]
    Gamma = np.zeros((4, 4, 4))  # Gamma^lambda_mu_nu definition
    for lam in range(4):
        for mu in range(4):
            for nu in range(4):
                sum_terms = 0.0
                for sigma in range(4):
                    if sigma < 3:
                        key_x = (mu, nu, 'x')
                        sum_terms += g_inv[lam, sigma] * (partials[key_x] + partials[key_x] - partials[key_x])
                Gamma[lam, mu, nu] = 0.5 * sum_terms
    return Gamma

def geodesic_equations(t, Y, M, a):
    """
    Defines the geodesic equations in Kerr-Schild coordinates.
    """
    x, y, z, px, py, pz = Y  # Position and momentum components
    r = compute_r(x, y, z)
    g = g_mu_nu(x, y, z)
    Gamma = compute_christoffel_symbols(x, y, z)
    
    # Set derivatives for spatial coordinates
    dxdt, dydt, dzdt = px, py, pz

    # Initialize momentum derivatives
    dpxdt, dpydt, dpzdt = 0.0, 0.0, 0.0

    # Compute derivatives of momentum components using the Christoffel symbols
    for mu in range(4):
        for nu in range(4):
            dpxdt += -Gamma[1, mu, nu] * (px if mu == 0 else py if mu == 1 else pz) * (px if nu == 0 else py if nu == 1 else pz)
            dpydt += -Gamma[2, mu, nu] * (px if mu == 0 else py if mu == 1 else pz) * (px if nu == 0 else py if nu == 1 else pz)
            dpzdt += -Gamma[3, mu, nu] * (px if mu == 0 else py if mu == 1 else pz) * (px if nu == 0 else py if nu == 1 else pz)

    return [dxdt, dydt, dzdt, dpxdt, dpydt, dpzdt]

def integrate_geodesic(x0, y0, z0, px0, py0, pz0, max_distance):
    """
    Integrates the geodesic equations starting from an initial position and momentum.
    Stops if the geodesic reaches the event horizon or exceeds max_distance.
    """
    def stop_condition(t, Y, M, a):
        x, y, z = Y[0], Y[1], Y[2]
        r = compute_r(x, y, z)
        if r <= 2 * M:  # Horizon check
            return 0
        elif np.sqrt(x**2 + y**2 + z**2) > max_distance:
            return 0
        return 1
    
    stop_condition.terminal = True
    result = solve_ivp(geodesic_equations, [0, 1000], [x0, y0, z0, px0, py0, pz0], args=(M, a), events=stop_condition)
    return result

if __name__ == "__main__":
    # Initial conditions
    x0, y0, z0 = 10.0, 0.0, 0.0  # Camera position
    px0, py0, pz0 = -1.0, 0.0, 0.0  # Initial momentum
    max_distance = np.sqrt(x0**2 + y0**2 + z0**2)

    # Perform integration
    result = integrate_geodesic(x0, y0, z0, px0, py0, pz0, max_distance)

    # Plot geodesic path
    fig, ax = plt.subplots()
    ax.plot(result.y[0], result.y[1])
    plt.title('Null Geodesic Path')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.show()