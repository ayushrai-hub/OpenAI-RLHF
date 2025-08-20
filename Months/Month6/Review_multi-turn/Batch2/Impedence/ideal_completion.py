import numpy as np

def compute_neutral_impedance(v: np.ndarray, i_a: np.ndarray, i_b: np.ndarray) -> float:
    v = np.asarray(v)
    i_a = np.asarray(i_a)
    i_b = np.asarray(i_b)
    # Check for empty arrays
    if v.size == 0 or i_a.size == 0 or i_b.size == 0:
        return float('nan')
    # Check for shape mismatch
    if v.shape != i_a.shape or v.shape != i_b.shape or i_a.shape != i_b.shape:
        return float('nan')
    # Check for negative values
    if np.any(v < 0) or np.any(i_a < 0) or np.any(i_b < 0):
        return float('nan')
    # Compute neutral current
    i_n = i_a - i_b
    # Check for zero currents in denominator
    if np.any(i_n == 0):
        return float('nan')
    # Compute line to neutral voltage
    v_ln = v / 2.0
    impedance = np.abs(v_ln / i_n)
    # Compute and return mean if array
    if np.ndim(impedance) > 0 and impedance.shape != ():
        return float(np.mean(impedance))
    else:
        return float(impedance)
