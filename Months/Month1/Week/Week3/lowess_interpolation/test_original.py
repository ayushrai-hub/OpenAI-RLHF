from datetime import datetime, timedelta
import numpy as np
from typing import List, NamedTuple
from statsmodels.nonparametric.smoothers_lowess import lowess

class Analysis(NamedTuple):
    time: datetime
    ratio: float
    error: float
    name: str
    type: str
    active: bool

class Blanks(NamedTuple):
    time: datetime
    ratio: float
    error: float
    active: bool

class RE_as_HB(NamedTuple):
    pass

def lowess_interpolation(sequence_data: List[Analysis], blanks: List[Blanks], RE_as_HBs: List[RE_as_HB], smooth: bool = True) -> List[dict]:
    results = []

    # Determine smoothing factor
    frac = 0.38 if smooth else 0.31

    # Extract times, ratios, and errors for blanks
    t0 = blanks[0].time
    t_blanks = np.array([(blank.time - t0).total_seconds() for blank in blanks if blank.active])
    R_blanks = np.array([blank.ratio for blank in blanks if blank.active])
    R_blanks_err = np.array([blank.error for blank in blanks if blank.active])

    # LOWESS interpolation over all blanks
    lowess_result = lowess(R_blanks, t_blanks, frac=frac, it=10, return_sorted=False)

    # Interpolate for each unknown in the sequence_data
    for analysis in sequence_data:
        if analysis.type == "unknown" and analysis.active:
            unknown_time = (analysis.time - t0).total_seconds()
            blank_correction = np.interp(unknown_time, t_blanks, lowess_result)

            # Refine the error propagation
            weights = 1 / (R_blanks_err**2)
            normalized_weights = weights / np.sum(weights)
            blank_corr_error = np.sqrt(np.sum((normalized_weights * R_blanks_err) ** 2))

            hovlabel = (
                f"{analysis.name}\n"
                f"Ratio: {analysis.ratio:.4f} ± {analysis.error:.4f}\n"
                f"Blank Correction: {blank_correction:.4f} ± {blank_corr_error:.4f}"
            )

            # Store result
            results.append({
                "time": analysis.time,
                "interpolated_ratio": blank_correction,
                "interpolated_error": blank_corr_error,
                "hovlabel": hovlabel
            })

    return results
