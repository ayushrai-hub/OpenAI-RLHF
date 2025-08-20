
import numpy as np
from scipy.optimize import least_squares

def compute_neutral_impedance(v: np.ndarray, i_a: np.ndarray, i_b: np.ndarray) -> float:
    """
    Compute the neutral impedance magnitude from time series information.

    Parameters:
    v   : array-like, RMS voltage between lines (V)
    i_a : array-like, RMS current on the first phase (A)
    i_b : array-like, RMS current on the second phase (A)

    Returns:
    Z_n_calc : float, Computed neutral impedance magnitude (Ohms)
    """
    # Convert inputs into numpy arrays
    v = np.asarray(v)
    i_a = np.asarray(i_a)
    i_b = np.asarray(i_b)
    
    # Voltage from line to neutral
    V_s = v / 2  # Assuming equal transformer splits

    # Initial guess for Z_n
    Z_n_guess = 0.1  # Ohms

    # Define the residual function for least squares
    def residual(Z_n, V_s, I1_observed, I2_observed):
        V_n = Z_n * (I1_observed + I2_observed)
        # Assuming constant load impedances R1 and R2
        # Calculate R1 and R2 using initial observations
        R1 = (V_s[0] - V_n[0]) / I1_observed[0]
        R2 = (-V_s[0] - V_n[0]) / I2_observed[0]
        # Model predictions for currents
        I1_modeled = (V_s - V_n) / R1
        I2_modeled = (-V_s - V_n) / R2
        # Difference between observed and predicted currents
        res_I1 = I1_observed - I1_modeled
        res_I2 = I2_observed - I2_modeled
        # Combine residuals
        return np.concatenate((res_I1, res_I2))

    # Find Z_n using least squares optimization
    result = least_squares(
        residual, Z_n_guess, args=(V_s, i_a, i_b), bounds=(0, np.inf)
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
