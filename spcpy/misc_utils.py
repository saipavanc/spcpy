import numpy as np
from typing import Tuple

def despike(phi_vals, freqs, slope_threshold=0.25e-5, width=10e-2) -> Tuple[np.ndarray, np.ndarray]:
    """
    Remove spikes from a curve by filtering out points, and their neighbouring points, 
    with a slope above slope_threshold.

    Args:
        phi_vals (array): pts on x-axis
        freqs (array): pts on y-axis
        slope_threshold (float, optional): The threshold of slope over which peaks will be removed. 
                                            Defaults to 0.25e-5.
        width (float, optional): The width on x-axis over which the neighbouring pts will be removed.
                                    Defaults to 10e-2.

    Returns:
        Tuple[np.ndarray, np.ndarray]: phi_vals and freqs after removing spikes.
    """
    slopes = np.abs(np.gradient(freqs))
    idxs_slopes = [idx for idx in range(len(slopes)) if slopes[idx] > slope_threshold]
    # width of peaks or dips in units of the x-axis
    dx = phi_vals[1] - phi_vals[0]
    number_of_pts_around_peaks = int(width/dx)
    idxs_remove = idxs_slopes.copy()

    for idx in idxs_slopes:
        additional_pts = np.array([idx + i for i in range(-number_of_pts_around_peaks, number_of_pts_around_peaks)])
        additional_pts = additional_pts[(additional_pts >= 0) & (additional_pts < len(phi_vals))]
        idxs_remove.extend(additional_pts)

    idxs_remove = np.sort(np.unique(idxs_remove))
    idxs_filtered = [idx for idx in range(len(phi_vals)) if idx not in idxs_remove]
    return phi_vals[idxs_filtered], freqs[idxs_filtered]