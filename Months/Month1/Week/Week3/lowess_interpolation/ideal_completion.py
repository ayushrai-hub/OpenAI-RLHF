import numpy as np
from datetime import datetime, timedelta
from typing import List, NamedTuple
from statsmodels.nonparametric.smoothers_lowess import lowess

# Mock classes to replace custom imports
class Analysis(NamedTuple):
    timestamp: datetime
    ratio: float
    ratio_err: float
    label: str
    analysis_type: str
    active: bool

class Blanks(NamedTuple):
    timestamp: datetime
    ratio: float
    error: float
    use: bool

class RE_as_HB(NamedTuple):
    pass

def is_active_re_as_hb(analysis, RE_as_HBs):
    # Mocked function, always returns False for simplicity
    return False

def tricube(x):
    return np.where(np.abs(x) <= 1, (1 - np.abs(x)**3)**3, 0)

def lowess_interpolation(
    sequence_data: List[Analysis],
    blanks: List[Blanks],
    RE_as_HBs: List[RE_as_HB],
    smooth: bool,
    it: int = 10,
):
    results = []
    frac = 0.38 if smooth else 0.25
    t0 = blanks[0].timestamp
    t_blanks = np.array([(blank.timestamp - t0).total_seconds() for blank in blanks if blank.use])
    R_blanks = np.array([blank.ratio for blank in blanks if blank.use])
    R_blanks_err = np.array([blank.error for blank in blanks if blank.use])
    
    lowess_result = lowess(R_blanks, t_blanks, frac=frac, it=it, return_sorted=False)
    
    for analysis in sequence_data:
        if analysis.analysis_type == "unknown" and analysis.active and not is_active_re_as_hb(analysis, RE_as_HBs):
            unknown_time = (analysis.timestamp - t0).total_seconds()
            blank_correction = np.interp(unknown_time, t_blanks, lowess_result)
            
            # Sliding window approach
            window_size = max(3, int(len(t_blanks) * (frac * 1.2 if smooth else frac * 0.8)))  # Ensure at least 3 points in the window
            distances = np.abs(t_blanks - unknown_time)
            window_indices = np.argsort(distances)[:window_size]
            
            # Apply tricube weighting
            max_distance = np.max(distances[window_indices])
            weights = tricube(distances[window_indices] / max_distance)
            
            # Normalize weights and calculate error
            normalized_weights = weights / np.sum(weights)
            local_variance = np.sum(normalized_weights * (R_blanks[window_indices] - lowess_result[window_indices])**2)
            blank_corr_error = np.sqrt(local_variance)
            
            # Ensure non-zero error by adding a small constant
            blank_corr_error = max(blank_corr_error, 1e-6)
            
            hovlabel = (
                f"{analysis.label}\n"
                f"Ratio: {analysis.ratio:.4f} ± {analysis.ratio_err:.4f}\n"
                f"Blank Correction: {blank_correction:.4f} ± {blank_corr_error:.4f}"
            )
            
            results.append({
                "time": analysis.timestamp,
                "interpolated_ratio": blank_correction,
                "interpolated_error": blank_corr_error,
                "hovlabel": hovlabel
            })
    
    return results

# Example usage
if __name__ == "__main__":
    # Create mock data
    now = datetime.now()
    blanks = [Blanks(now + timedelta(hours=i), 1.0 + 0.1 * i, 0.05, True) for i in range(10)]
    sequence_data = [Analysis(now + timedelta(hours=i+0.5), 1.5 + 0.2 * i, 0.1, f"Sample {i}", "unknown", True) for i in range(9)]
    RE_as_HBs = []

    # Run the interpolation
    results = lowess_interpolation(sequence_data, blanks, RE_as_HBs, smooth=True)
    
    # Print results
    for result in results:
        print(f"Time: {result['time']}, Interpolated Ratio: {result['interpolated_ratio']:.4f} ± {result['interpolated_error']:.4f}")