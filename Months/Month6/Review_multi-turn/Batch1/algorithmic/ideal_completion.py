import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

def calculate_optimal_prices(s_min, s_max, num_s, c, sigma_e):
    """
    Calculate optimal prices for a range of scalar variables S_i.

    Parameters:
    s_min (float): Minimum value of S_i.
    s_max (float): Maximum value of S_i.
    num_s (int): Number of S_i values to evaluate.
    c (float): Marginal cost.
    sigma_e (float): Standard deviation of the error term e_i.

    Returns:
    tuple: A tuple containing the array of S_i values and the corresponding optimal prices.
    """
    S_i_values = np.linspace(s_min, s_max, num_s)
    optimal_prices = []

    # Function to calculate the derivative of the profit function
    def profit_derivative(p, S_i):
        return (1 - norm.cdf(p - 1 - S_i, scale=sigma_e)) - (p - c) * norm.pdf(p - 1 - S_i, scale=sigma_e) / sigma_e

    # Function to find optimal price for a given S_i
    def find_optimal_price(S_i, p_min=0, p_max=5, epsilon=1e-5):
        p_values = np.linspace(p_min, p_max, 1000)
        derivatives = profit_derivative(p_values, S_i)
        
        # Find where the derivative crosses zero
        sign_changes = np.where(np.diff(np.sign(derivatives)))[0]
        
        if len(sign_changes) == 0:
            # No zero crossing found, return p that gives max profit
            profits = (p_values - c) * (1 - norm.cdf(p_values - 1 - S_i, scale=sigma_e))
            return p_values[np.argmax(profits)]
        
        # Bisection method to refine the root
        low, high = p_values[sign_changes[0]], p_values[sign_changes[0] + 1]
        while high - low > epsilon:
            mid = (low + high) / 2
            if profit_derivative(mid, S_i) > 0:
                low = mid
            else:
                high = mid
        return (low + high) / 2

    for S_i in S_i_values:
        optimal_price = find_optimal_price(S_i)
        optimal_prices.append(optimal_price)

    return S_i_values, np.array(optimal_prices)

def plot_optimal_prices(s_values, p_optimal):
    """
    Plot the optimal prices against S_i values.

    Parameters:
    s_values (array-like): Array of S_i values.
    p_optimal (array-like): Array of optimal prices corresponding to S_i values.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(s_values, p_optimal, label='Optimal Price')
    plt.title('Optimal Price as a Function of S_i')
    plt.xlabel('S_i')
    plt.ylabel('Optimal Price')
    plt.grid(True)
    plt.legend()
    plt.close()
