import numpy as np
from analysis_class import Analysis
from typing import List
from sequence.blanks.blank_classes import Blanks, RE_as_HB
from statsmodels.nonparametric.smoothers_lowess import lowess
from sequence.reextracts import is_active_re_as_hb

def lowess_interpolation(
    sequence_data: List[Analysis],
    blanks: List[Blanks],
    RE_as_HBs: List[RE_as_HB],
    smooth: bool,
    it=10,
):
    results = []

    # Determine smoothing factor
    frac = 0.38 if smooth else 0.31

    # Extract times, ratios, and errors for blanks
    t0 = blanks[0].timestamp
    t_blanks = np.array([(blank.timestamp - t0).total_seconds() for blank in blanks if blank.use])
    R_blanks = np.array([blank.ratio for blank in blanks if blank.use])
    R_blanks_err = np.array([blank.error for blank in blanks if blank.use])

    # LOWESS interpolation over all blanks
    lowess_result = lowess(R_blanks, t_blanks, frac=frac, it=it, return_sorted=False)

    # Interpolate for each unknown in the sequence_data
    for analysis in sequence_data:
        if (
            analysis.analysis_type == "unknown"
            and analysis.active
            and not is_active_re_as_hb(analysis, RE_as_HBs)
        ):
            unknown_time = (analysis.timestamp - t0).total_seconds()
            blank_correction = np.interp(unknown_time, t_blanks, lowess_result)

            # Refine the error propagation
            weights = 1 / (R_blanks_err**2)
            normalized_weights = weights / np.sum(weights)
            blank_corr_error = np.sqrt(np.sum((normalized_weights * R_blanks_err) ** 2))

            hovlabel = (
                f"{analysis.label}\n"
                f"Ratio: {analysis.ratio:.4f} ± {analysis.ratio_err:.4f}\n"
                f"Blank Correction: {blank_correction:.4f} ± {blank_corr_error:.4f}"
            )

            # Store result
            results.append({
                "time": analysis.timestamp,
                "interpolated_ratio": blank_correction,
                "interpolated_error": blank_corr_error,
                "hovlabel": hovlabel
            })

    return results
