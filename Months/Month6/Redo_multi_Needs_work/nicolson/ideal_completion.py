import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

def crank_nicolson_2D_sphere(t_limit, radius, theta=np.pi, d_radius=0.01,
                              d_theta=0.01, d_time=0.001, beta=1.0,
                              Initial_Temp=300.0, Energy=0.0,
                              impulse_time=0.1, conv=1.0,
                              specific_heat=1.0, density=1.0):
    # Setup space grids
    nr = int(radius/d_radius) + 1
    nth = int(theta/d_theta) + 1
    r = np.linspace(d_radius, radius, nr)  # Avoid r = 0
    th = np.linspace(0, theta, nth)
    T = np.full((nr, nth), Initial_Temp)
    alpha = beta/(specific_heat*density)
    lam_r = alpha * d_time/(2*d_radius**2)
    # Build CN matrices for radial direction
    diagA = np.ones(nr)*(1 + 2*lam_r)
    offA = -lam_r*np.ones(nr-1)
    diagA[1:] += lam_r/(np.arange(1,nr))
    diagB = np.ones(nr)*(1 - 2*lam_r)
    offB = lam_r*np.ones(nr-1)
    diagB[1:] -= lam_r/(np.arange(1,nr))
    A_r = diags([diagA, offA, offA],[0,-1,1],shape=(nr,nr)).tocsc()
    B_r = diags([diagB, offB, offB],[0,-1,1],shape=(nr,nr)).tocsc()
    t = 0.0
    times = []
    temps = []
    while t < t_limit + 1e-12:
        times.append(float(t))
        temps.append(T.copy())
        # Add energy if impulse
        if t < impulse_time:
            T += Energy*d_time/(specific_heat*density)
        # Solve radial direction for each theta
        T_new = T.copy()
        for j in range(nth):
            rhs = B_r.dot(T[:,j])
            T_new[:,j] = spsolve(A_r, rhs)
        T = T_new
        t += d_time
    return np.array(times), np.array(temps)
