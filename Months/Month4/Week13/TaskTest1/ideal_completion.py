#ideal_completion.py

import numpy as np
from scipy.linalg import norm
from scipy.optimize import minimize

def execute_DualTri(y_opt_ini, y_start, Total_Iter, cost_function, Total_Nodes, Data_Size, nu, nu_adjust, gamma_rate, W_link_matrix, requires_central_solution, return_y, Q, a, Q_trial, a_trial):
    # Initialize variables
    Data_Size_values = np.array([Data_Size + a[k].shape[0] if cost_function in ['MC_adjust', 'L1_adjust'] else Data_Size for k in range(Total_Nodes)])
    y_k = [np.concatenate((y_start, np.zeros(a[k].shape[0]))) if cost_function in ['MC_adjust', 'L1_adjust'] else y_start.copy() for k in range(Total_Nodes)]
    
    # Adjust Q and identity matrices for specific cost functions
    if cost_function in ['MC_adjust', 'L1_adjust']:
        Q = [np.hstack((Q[k], np.eye(a[k].shape[0]))) for k in range(Total_Nodes)]
    identity_zero_matr = [np.hstack((np.eye(Data_Size), np.zeros((Data_Size, Data_Size_values[k] - Data_Size)))) for k in range(Total_Nodes)]

    # Initialize algorithm variables
    theta = np.logical_or(W_link_matrix, np.eye(Total_Nodes)).astype(int)
    z_k = [np.zeros(Q[k].shape[0]) for k in range(Total_Nodes)]
    u_k = [[np.zeros(Data_Size) if W_link_matrix[m, k] == 1 else 0 for m in range(Total_Nodes)] for k in range(Total_Nodes)]

    # Calculate step sizes
    beta, alpha = calculate_step_sizes(Q, nu, nu_adjust, W_link_matrix, cost_function)

    # Calculate global optimization if required
    y_opt_summary = Compute_y(y_opt_ini, Q, a, max(nu), max(nu_adjust), gamma_rate, cost_function) if requires_central_solution else np.zeros(Data_Size)

    y_error_duration = np.zeros((Total_Nodes, Total_Iter))
    y_avgconsensus_duration = np.zeros((Total_Nodes, Total_Iter))

    # Main iteration loop
    for m in range(Total_Iter):
        for v in range(Total_Nodes):
            sum_u_neighbors = calculate_sum_u_neighbors(v, Total_Nodes, W_link_matrix, u_k, y_k, theta, Data_Size_values, cost_function, a)
            z = z_k[v] + beta[v] * Q[v] @ y_k[v]
            z_new, y_k1 = update_variables(v, z, beta[v], Q[v], y_k[v], alpha[v], sum_u_neighbors, nu[v], nu_adjust[v], gamma_rate, cost_function, a[v])

            z_k[v] = z_new + beta[v] * Q[v] @ (y_k1 - y_k[v])
            y_k[v] = y_k1

            update_u_k(v, Total_Nodes, W_link_matrix, u_k, theta, Data_Size_values, cost_function, a, y_k)

        y_opt, y_error_duration[:, m], y_avgconsensus_duration[:, m] = calculate_metrics(Total_Nodes, identity_zero_matr, y_k, y_opt_ini, y_opt_summary, return_y, Q_trial, a_trial)

        if check_convergence(y_k, cost_function, m):
            break

    return y_error_duration, y_avgconsensus_duration, y_opt_summary, y_opt

def calculate_step_sizes(Q, nu, nu_adjust, W_link_matrix, cost_function):
    beta = np.full(len(Q), 0.065)
    alpha = np.zeros(len(Q))
    for k, Q_k in enumerate(Q):
        L = calculate_lipschitz(cost_function, nu[k], nu_adjust[k], np.linalg.norm(Q_k.T @ Q_k))
        alpha[k] = 0.09 / (L / 2 + np.linalg.norm(beta[k] * Q_k.T @ Q_k) + np.sum(W_link_matrix[k]))
    return beta, alpha

def calculate_lipschitz(cost_function, nu, nu_adjust, Q_norm):
    if cost_function == 'Exponential':
        return 2 * nu * Q_norm
    elif cost_function == 'FairPotential':
        return 5 * nu * Q_norm
    elif cost_function == 'Hyperbolic':
        return (1 / nu) * Q_norm
    elif cost_function in ['MC_adjust', 'L1_adjust', 'MC', 'Huber']:
        return 2 * Q_norm + nu + nu_adjust
    else:
        return nu * Q_norm

def Compute_y(y_opt_ini, Q, a, max_nu, max_nu_adjust, gamma_rate, cost_function):
    def objective_function(y):
        total_cost = 0
        for Q_i, a_i in zip(Q, a):
            residual = Q_i @ y - a_i
            if cost_function == 'L2':
                total_cost += 0.5 * max_nu * np.sum(residual**2)
            elif cost_function in ['MC', 'L1', 'MC_adjust', 'L1_adjust']:
                total_cost += max_nu * np.sum(np.abs(residual))
            elif cost_function == 'Huber':
                total_cost += np.sum(np.where(np.abs(residual) <= max_nu,
                                              0.5 * residual**2,
                                              max_nu * (np.abs(residual) - 0.5 * max_nu)))
            elif cost_function == 'Tukey':
                c = max_nu_adjust
                total_cost += np.sum(np.where(np.abs(residual) <= c,
                                              (c**2 / 6) * (1 - (1 - (residual/c)**2)**3),
                                              c**2 / 6))
            elif cost_function == 'Exponential':
                total_cost += np.sum(np.exp(gamma_rate * np.abs(residual)) - 1) / gamma_rate
            elif cost_function == 'Hyperbolic':
                total_cost += np.sum(np.log(np.cosh(gamma_rate * residual))) / gamma_rate
            elif cost_function == 'FairPotential':
                c = max_nu_adjust
                total_cost += c**2 * np.sum(np.abs(residual) / c - np.log(1 + np.abs(residual) / c))
        return total_cost

    result = minimize(objective_function, y_opt_ini, method='BFGS')
    return result.x if result.success else y_opt_ini

def calculate_sum_u_neighbors(v, Total_Nodes, W_link_matrix, u_k, y_k, theta, Data_Size_values, cost_function, a):
    sum_u_neighbors = np.zeros(Data_Size_values[v])
    for p in range(Total_Nodes):
        if W_link_matrix[v, p] == 1:
            B_v = np.eye(Data_Size_values[v])
            B_p = np.eye(Data_Size_values[p])
            u_k[v][p] = 0.5 * (u_k[v][p] + u_k[p][v]) + 0.5 * theta[v, p] * (B_v @ y_k[v] + B_p @ y_k[p])
            sum_u_neighbors += B_v.T @ u_k[v][p]
    return sum_u_neighbors

def update_variables(v, z, beta, Q, y_k, alpha, sum_u_neighbors, nu, nu_adjust, gamma_rate, cost_function, a):
    if cost_function in ['MC', 'L1', 'MC_adjust', 'L1_adjust']:
        z_new = z - beta * np.sign(z - a) * np.maximum(np.abs(z - a) - beta, 0)
    elif cost_function == 'L2':
        z_new = z - beta * (z - a) / (1 + 2 * beta)
    elif cost_function == 'Huber':
        z_new = z - beta * np.where(np.abs(z - a) <= nu, (z - a) / (1 + beta), nu * np.sign(z - a))
    else:
        z_new = z

    grad = grad_H(y_k, nu, nu_adjust, gamma_rate, cost_function, Q, a)
    y_k1 = y_k - alpha * (Q.T @ z_new + sum_u_neighbors + grad)
    
    return z_new, y_k1

def update_u_k(v, Total_Nodes, W_link_matrix, u_k, theta, Data_Size_values, cost_function, a, y_k):
    for p in range(Total_Nodes):
        if W_link_matrix[v, p] == 1:
            B = np.eye(Data_Size_values[v])
            u_k[v][p] += theta[v, p] * B @ y_k[v]

def calculate_metrics(Total_Nodes, identity_zero_matr, y_k, y_opt_ini, y_opt_summary, return_y, Q_trial, a_trial):
    y_opt = sum(identity_zero_matr[v] @ y_k[v] for v in range(Total_Nodes)) / Total_Nodes
    if return_y:
        y_error = np.array([norm(Q_trial @ identity_zero_matr[v] @ y_k[v] - a_trial) for v in range(Total_Nodes)])
    else:
        y_error = np.array([norm(identity_zero_matr[v] @ y_k[v] - y_opt_ini)**2 / (norm(y_opt_ini)**2) for v in range(Total_Nodes)])
    y_avgconsensus = np.array([norm(identity_zero_matr[v] @ y_k[v] - y_opt_summary) / norm(y_opt_summary) for v in range(Total_Nodes)])
    return y_opt, y_error, y_avgconsensus

def check_convergence(y_k, cost_function, m):
    convergence_limit = 1e-6 if cost_function in ['Huber', 'FairPotential', 'Tukey'] else 1e-5
    return all(np.linalg.norm(y_k[v] - y_k[0], np.inf) <= convergence_limit for v in range(1, len(y_k))) and m >= 10

def grad_H(y, nu, nu_adjust, gamma_rate, cost_function, Q, a):
    if cost_function in ['MC', 'MC_adjust']:
        return nu * y
    elif cost_function in ['L1', 'L1_adjust']:
        return nu * np.sign(y)
    elif cost_function == 'L2':
        return 2 * nu * y
    elif cost_function == 'Huber':
        return nu * np.where(np.abs(y) <= 1, y, np.sign(y))
    elif cost_function == 'Tukey':
        Qy_a = Q @ y - a
        return Q.T @ np.where(np.abs(Qy_a) <= nu_adjust, Qy_a * (1 - (Qy_a/nu_adjust)**2)**2, np.zeros_like(Qy_a))
    elif cost_function == 'Exponential':
        return nu * np.exp(gamma_rate * y)
    elif cost_function == 'Hyperbolic':
        return nu * np.tanh(gamma_rate * y)
    elif cost_function == 'FairPotential':
        Qy_a = Q @ y - a
        return Q.T @ (Qy_a / (1 + np.abs(Qy_a) / nu_adjust))
    else:
        raise ValueError(f"Unknown cost function: {cost_function}")