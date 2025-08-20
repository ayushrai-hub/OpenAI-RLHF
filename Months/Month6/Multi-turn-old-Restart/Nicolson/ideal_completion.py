import numpy as np

def crank_nicolson_2D_sphere(t_limit: float,
                              radius: float,
                              theta: float,
                              d_radius: float,
                              d_theta: float,
                              d_time: float,
                              beta: float,
                              Initial_Temp: float,
                              Energy: float,
                              impulse_time: float,
                              conv: float,
                              specific_heat: float,
                              density: float):
    # Calculate grid sizes
    r_points = int(np.round(radius / d_radius)) + 1
    theta_points = int(np.round(theta / d_theta)) + 1
    # Ensure at least two points
    if r_points < 2: r_points = 2
    if theta_points < 2: theta_points = 2

    times = np.arange(0, t_limit + d_time, d_time)
    n_times = len(times)
    # If no time steps, return empty results
    if n_times == 0:
        return np.array([]), np.array([])

    # Initialize temperature array
    T = np.ones((n_times, r_points, theta_points)) * Initial_Temp

    # Time stepping
    for n in range(1, n_times):
        T_old = T[n-1].copy()
        T_half = T_old.copy()
        for i in range(1, r_points-1):
            for j in range(1, theta_points-1):
                lap_r = (T_old[i+1,j] - 2*T_old[i,j] + T_old[i-1,j]) / (d_radius**2)
                lap_t = (T_old[i,j+1] - 2*T_old[i,j] + T_old[i,j-1]) / (d_theta**2)
                T_half[i,j] = T_old[i,j] + beta * d_time * (lap_r + lap_t)
        if times[n] <= impulse_time:
            T_half += (Energy/(specific_heat*density*radius*theta)) * d_time

        T_new = 0.5*(T_old + T_half)
        T_new[0,:] = T_new[1,:]
        T_new[-1,:] = T_new[-2,:]
        T_new[:,0] = T_new[:,1]
        T_new[:,-1] = T_new[:,-2]
        T[n] = T_new

    # Normalize
    T_min = T.min()
    T_max = T.max()
    if T_max - T_min != 0:
        T_norm = (T - T_min) / (T_max - T_min)
    else:
        T_norm = T

    return T_norm, times
