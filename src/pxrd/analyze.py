"""
Diffractogram analysis functions
"""
# --- Imports

# Standard library
from typing import Optional

# External packages
from BaselineRemoval import BaselineRemoval
import numpy as np
import scipy


# --- Constants

# Data cleaning parameters
_ZHANG_FIT_REPETITIONS = 100
_SG_FILTER_WINDOW = 5
_SG_FILTER_ORDER = 3

# Peak detection parameters
_MIN_HEIGHT_QUANTILE = 0.8
_PROMINENCE_QUANTILE = 0.6

# --- Functions


def clean_up_diffractogram(
    raw_intensity: np.ndarray,
    sg_filter_window: int = _SG_FILTER_WINDOW,
    sg_filter_order: int = _SG_FILTER_ORDER,
) -> np.ndarray:
    """
    Clean up raw diffractogram to prepare it for analysis.

    `clean_up_diffractogram()` performs the following cleanup steps.

    * Baseline correction using the algorithm developed by Zhang, Chen, and Liang (2010).

    * Noise removal using the Savitzky-Golay filter.

    Arguments
    ---------
    raw_intensity: raw diffractogram intensity data (usually counts)

    sg_filter_window: width of window to use for Savitzky-Golay filter

    sg_filter_order: order of polynomial to use for Savitzky-Golay filter

    Return Value
    ------------
    cleaned diffractogram
    """
    # --- Check arguments
    #
    # Notes
    # -----
    # * Savitzky-Golay filter parameters are checked by scipy.signal.savgol_filter()

    if raw_intensity.size == 0:
        raise ValueError("'raw_intensity' should not be empty")

    if len(raw_intensity.shape) > 1:
        raise ValueError("'raw_intensity' should be a 1D vector")

    # --- Clean data

    # Remove baseline
    intensity = BaselineRemoval(raw_intensity).ZhangFit(
        repitition=_ZHANG_FIT_REPETITIONS
    )

    # Apply Savitzky-Golay filter to remove high frequency noise
    intensity = scipy.signal.savgol_filter(intensity, sg_filter_window, sg_filter_order)

    return intensity


def find_peaks(
    intensity: np.ndarray,
    min_height_quantile: float = _MIN_HEIGHT_QUANTILE,
    prominence_quantile: float = _PROMINENCE_QUANTILE,
    horizontal_scale_units: Optional[float] = None,
) -> (np.ndarray, np.ndarray):
    """
    TODO

    Arguments
    ---------
    intensity: diffractogram intensity data

    min_height_quantile: TODO

    prominence_quantile: TODO

    Return value
    ------------
    peak_indices: indices of the `intensity` where peaks are located

    peak_widths: widths of peaks. If `horizontal_scale_units` is not `None`, peak widths
        are computed in the specified units; otherwise, peak widths are computed assuming
        an arbitrary horizontal scale where consecutive `intensity` values are separated
        by 1 unit.

    Notes
    -----
    * TODO: uniform spacing of horizontal scale when `units` is specified
    """
    # --- Check arguments

    # TODO

    # --- Find peaks

    # Compute peak finding parameters
    min_height = np.quantile(intensity, q=min_height_quantile)
    prominence = np.quantile(intensity, q=prominence_quantile)

    # Identify peaks
    peaks, properties = scipy.signal.find_peaks(
        intensity, height=min_height, prominence=prominence
    )

    # Compute peak widths
    widths, _, _, _ = scipy.signal.peak_widths(intensity, peaks)

    # TODO: modify to support non-uniform horizontal scales
    # delta_2_theta = data["2-theta"][1] - data["2-theta"][0]
    peak_widths = widths

    return peaks, peak_widths
