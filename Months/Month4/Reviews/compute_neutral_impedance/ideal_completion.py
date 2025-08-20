#ideal_completion.py
import numpy as np
from scipy.optimize import least_squares

def compute_neutral_impedance(v, i_a, i_b):
    """
    Compute the neutral impedance magnitude from time series information.

    Parameters:
    v   : array-like, RMS voltage between lines (V)
    i_a : array-like, RMS current on the first phase (A)
    i_b : array-like, RMS current on the second phase (A)

    Returns:
    Z_n_calc : float, Computed neutral impedance magnitude (Ohms) or NaN for invalid inputs
    """
    # Convert inputs into numpy arrays
    v = np.asarray(v)
    i_a = np.asarray(i_a)
    i_b = np.asarray(i_b)
    
    # Input validation
    if v.size == 0 or i_a.size == 0 or i_b.size == 0 or v.size != i_a.size or v.size != i_b.size:
        return float('nan')
    if np.isnan(v).any() or np.isnan(i_a).any() or np.isnan(i_b).any():
        return float('nan')
    if np.isinf(v).any() or np.isinf(i_a).any() or np.isinf(i_b).any():
        return float('inf')
    if (v < 0).any() or (i_a < 0).any() or (i_b < 0).any():
        return float('nan')
    if i_a[0] == 0 or i_b[0] == 0:
        return float('nan')

    # Voltage from line to neutral
    V_s = v / 2

    # Improved initial guess for Z_n based on median observed currents
    initial_current_sum = np.median(i_a + i_b)
    Z_n_guess = 0.01 if initial_current_sum == 0 else np.median(V_s) / initial_current_sum

    # Estimate initial load resistances R1 and R2
    R1_initial = (V_s[0] - Z_n_guess * (i_a[0] + i_b[0])) / i_a[0]
    R2_initial = (-V_s[0] - Z_n_guess * (i_a[0] + i_b[0])) / i_b[0]

    # Define the residual function for least squares
    def residual(Z_n, V_s, I1_observed, I2_observed, R1, R2):
        V_n = Z_n * (I1_observed + I2_observed)
        # Model predictions for currents using vectorized calculations
        I1_modeled = np.divide(V_s - V_n, R1, where=R1 != 0)
        I2_modeled = np.divide(-V_s - V_n, R2, where=R2 != 0)
        # Return summed residuals for both phases
        return (I1_observed - I1_modeled) + (I2_observed - I2_modeled)

    # Run least squares optimization to find Z_n
    result = least_squares(
        residual, Z_n_guess, args=(V_s, i_a, i_b, R1_initial, R2_initial), bounds=(0, np.inf)
    )
    
    Z_n_calc = result.x[0]
    return Z_n_calc

# Testing the function with placeholder data
if __name__ == "__main__":
    # Placeholder time series data points
    data_points = 1000  # Number of entries
    v = np.full(data_points, 240.0)  # RMS voltage between lines (V)
    i_a = np.random.normal(10, 0.5, data_points)  # Current on first phase (A)
    i_b = np.random.normal(8, 0.5, data_points)   # Current on second phase (A)

    # Compute neutral impedance
    Z_n_computed = compute_neutral_impedance(v, i_a, i_b)
    print(f"Computed Neutral Impedance: {Z_n_computed:.4f} Ohms")