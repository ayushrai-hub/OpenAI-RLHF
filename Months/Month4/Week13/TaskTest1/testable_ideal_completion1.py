
import numpy as np
from scipy.linalg import norm

def execute_DualTri(y_opt_ini, y_start, Total_Iter, cost_function, Total_Nodes, Data_Size, nu, nu_adjust, gamma_rate, W_link_matrix, requires_central_solution, return_y, Q, a, Q_trial, a_trial):
    Linear_Operator_Size = np.zeros(Total_Nodes)
    Data_Size_W = Data_Size
    identity_zero_matr = [None] * Total_Nodes
    y_start_cell = [None] * Total_Nodes
    Data_Size_values = Data_Size * np.ones(Total_Nodes)

    if cost_function != 'MC_adjust':
        for k in range(Total_Nodes):
            identity_zero_matr[k] = np.eye(Data_Size)
            y_start_cell[k] = y_start
            Linear_Operator_Size[k] = a[k].shape[0]
    
    if cost_function in ['MC_adjust', 'L1_adjust']:
        for k in range(Total_Nodes):
            Q_new = np.hstack((Q[k], np.eye(a[k].shape[0])))
            Q[k] = Q_new
            identity_zero_matr[k] = np.hstack((np.eye(Data_Size), np.zeros((Data_Size, a[k].shape[0]))))
            Data_Size_values[k] = Data_Size + a[k].shape[0]
            y_start_cell[k] = np.concatenate((y_start, np.zeros(a[k].shape[0])))
            Linear_Operator_Size[k] = a[k].shape[0]

    theta = np.zeros((Total_Nodes, Total_Nodes))
    alpha, beta = calculate_step_sizes(Q, nu, nu_adjust, W_link_matrix, cost_function)

    Total_Iter += 1

    z_new = [None] * Total_Nodes
    z_k = [None] * Total_Nodes
    y_k = [None] * Total_Nodes
    y_k1 = [None] * Total_Nodes
    y_gap = [None] * Total_Nodes
    u_k = [None] * Total_Nodes
    u_k1 = [None] * Total_Nodes
    u_k_changed = [None] * Total_Nodes

    for o in range(Total_Nodes):
        z_k[o] = np.zeros(Q[o].shape[0])
        y_k[o] = y_start_cell[o]
        y_k1[o] = np.zeros(Data_Size_values[o])
        y_gap[o] = np.zeros(Data_Size_values[o])

    for o in range(Total_Nodes):
        u_k[o] = [None] * Total_Nodes
        u_k1[o] = [None] * Total_Nodes
        u_k_changed[o] = [None] * Total_Nodes
        for m in range(Total_Nodes):
            if W_link_matrix[m, o] == 1:
                u_k[o][m] = np.zeros(Data_Size_W)
                u_k1[o][m] = np.zeros(Data_Size_W)
                u_k_changed[o][m] = np.zeros(Data_Size_W)
            else:
                u_k[o][m] = 0
                u_k1[o][m] = 0
                u_k_changed[o][m] = 0

    if requires_central_solution == 1:
        y_opt_summary = Compute_y(y_opt_ini, Q, a, max(nu), max(nu_adjust), gamma_rate, cost_function)
    else:
        y_opt_summary = np.zeros(Data_Size_W)

    for m in range(Total_Iter - 1):
        for v in range(Total_Nodes):
            sum_u_neighbors = calculate_sum_u_neighbors(v, Total_Nodes, W_link_matrix, u_k, y_k, theta, Data_Size_values, cost_function, a)
            z = z_k[v] + beta[v] * Q[v] @ y_k[v]
            z_new[v], y_k1[v] = update_variables(v, z, beta[v], Q[v], y_k[v], alpha[v], sum_u_neighbors, nu[v], nu_adjust[v], gamma_rate, cost_function, a[v])
            z_k[v] = z_new[v] + beta[v] * Q[v] @ (y_k1[v] - y_k[v])
            update_u_k(v, Total_Nodes, W_link_matrix, u_k, theta, Data_Size_values, cost_function, a, y_k)

        for v in range(Total_Nodes):
            y_gap[v] = y_k1[v] - y_k[v]
            y_k[v] = y_k1[v]
            for p in range(Total_Nodes):
                if W_link_matrix[v, p] == 1:
                    u_k[v][p] = u_k1[v][p]

        y_error_duration, y_avgconsensus_duration, y_opt = calculate_metrics(Total_Nodes, identity_zero_matr, y_k, y_opt_ini, y_opt_summary, return_y, Q_trial, a_trial)

        if check_convergence(y_gap, cost_function, m):
            break

    return y_error_duration, y_avgconsensus_duration, y_opt_summary, y_opt

def calculate_step_sizes(Q, nu, nu_adjust, W_link_matrix, cost_function):
    Total_Nodes = len(Q)
    beta = np.zeros(Total_Nodes)
    alpha = np.zeros(Total_Nodes)
    for o in range(Total_Nodes):
        Q_norm = norm(Q[o].T @ Q[o])
        Lipschitz_G = calculate_lipschitz(cost_function, nu[o], nu_adjust[o], Q_norm)
        step_scale_factor = 1
        beta[o] = step_scale_factor * 0.5 / (1e-6 + 2 * Q_norm)
        theta = np.logical_or(W_link_matrix, np.eye(Total_Nodes, dtype=bool)).astype(int)
        alpha[o] = 0.9 / (Lipschitz_G / 2 + norm(beta[o] * Q[o].T @ Q[o]) + np.sum(theta[o, :]))
    return alpha, beta

def calculate_lipschitz(cost_function, nu, nu_adjust, Q_norm):
    if cost_function == 'Exponential':
        return 2 * nu * Q_norm
    elif cost_function == 'FairPotential':
        return 5 * nu * Q_norm
    elif cost_function == 'Hyperbolic':
        return 1 / nu * Q_norm
    elif cost_function == 'Tukey':
        return nu_adjust + Q_norm
    elif cost_function in ['MC_adjust', 'L1_adjust']:
        return 2 * Q_norm + nu + nu_adjust
    else:
        return nu * Q_norm

def Compute_y(y_opt_ini, Q, a, max_nu, max_nu_adjust, gamma_rate, cost_function):
    # Assuming this function is implemented elsewhere
    pass

def calculate_sum_u_neighbors(v, Total_Nodes, W_link_matrix, u_k, y_k, theta, Data_Size_values, cost_function, a):
    sum_u_neighbors = 0
    for p in range(Total_Nodes):
        if W_link_matrix[v, p] == 1:
            sum_u_neighbors += B_Matrix(v, p, Data_Size_values[v], cost_function, a[v]).T @ u_k[v][p]
    return sum_u_neighbors

def update_variables(v, z, beta, Q, y_k, alpha, sum_u_neighbors, nu, nu_adjust, gamma_rate, cost_function, a):
    if cost_function in ['MC', 'L1', 'MC_adjust', 'L1_adjust']:
        param = {'z': a, 'output': 0}
        solve_prox = prox_l1(z / beta, 1 / beta, param)
        z_new = z - beta * solve_prox
        y_k1 = y_k - alpha * (Q.T @ z_new + sum_u_neighbors + grad_H(y_k, nu, nu_adjust, gamma_rate, cost_function, Q, a, 1))
    elif cost_function == 'L2':
        param = {'z': a, 'output': 0}
        solve_prox = prox_l2(z / beta, 1 / beta, param)
        z_new = z - beta * solve_prox
        y_k1 = y_k - alpha * (Q.T @ z_new + sum_u_neighbors + grad_H(y_k, nu, nu_adjust, gamma_rate, cost_function, Q, a, 1))
    # Additional cases for other cost functions...
    return z_new, y_k1

def update_u_k(v, Total_Nodes, W_link_matrix, u_k, theta, Data_Size_values, cost_function, a, y_k):
    for p in range(Total_Nodes):
        if W_link_matrix[v, p] == 1:
            u_k[v][p] = u_k[v][p] + theta[v, p] * B_Matrix(v, p, Data_Size_values[v], cost_function, a[v]) @ (y_k[v] - y_k[v])

def calculate_metrics(Total_Nodes, identity_zero_matr, y_k, y_opt_ini, y_opt_summary, return_y, Q_trial, a_trial):
    y_error_duration = np.zeros(Total_Nodes)
    y_avgconsensus_duration = np.zeros(Total_Nodes)
    y_opt = identity_zero_matr[0] @ np.zeros(y_k[0].shape)
    for v in range(Total_Nodes):
        if return_y:
            y_mean_duration = norm(Q_trial @ identity_zero_matr[v] @ y_k[v] - a_trial)
        y_error_duration[v] = norm(identity_zero_matr[v] @ y_k[v] - y_opt_ini) ** 2 / (norm(y_opt_ini) ** 2)
        y_avgconsensus_duration[v] = norm(identity_zero_matr[v] @ y_k[v] - y_opt_summary) / norm(y_opt_summary)
        y_opt += identity_zero_matr[v] @ y_k[v] / Total_Nodes
    return y_error_duration, y_avgconsensus_duration, y_opt

def check_convergence(y_gap, cost_function, m):
    convergence_limit = 1e-5
    if cost_function == 'Huber':
        convergence_limit = 1e-6
    elif cost_function in ['FairPotential', 'MC_adjust', 'MC']:
        convergence_limit = 1e-5
    elif cost_function == 'Tukey':
        convergence_limit = 1e-7
    if any(np.linalg.norm(yg, np.inf) > convergence_limit for yg in y_gap) or m < 10:
        return False
    return True

def grad_H(y, nu, nu_adjust, gamma_rate, cost_function, Q, a):
    # Assuming this function is implemented elsewhere
    pass

def prox_l1(z, t, param):
    # Placeholder for proximal operator implementation
    pass

def prox_l2(z, t, param):
    # Placeholder for proximal operator implementation
    pass

def B_Matrix(v, p, Data_Size_values, cost_function, a):
    # Placeholder for B_Matrix implementation
    pass
