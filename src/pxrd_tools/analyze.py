"""
Diffractogram analysis functions
"""
# --- Imports

# Standard library
import copy
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
_MIN_PROMINENCE_QUANTILE = 0.6

# --- Functions


def apply_diffractogram_corrections(
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

    # --- Preparations

    # Create copy of intensity for local processing
    intensity = copy.deepcopy(raw_intensity)

    # --- Clean data

    # Remove baseline
    intensity = BaselineRemoval(intensity).ZhangFit(repitition=_ZHANG_FIT_REPETITIONS)

    # Apply Savitzky-Golay filter to remove high frequency noise
    intensity = scipy.signal.savgol_filter(intensity, sg_filter_window, sg_filter_order)

    return intensity


def find_peaks(
    intensity: np.ndarray,
    min_height: Optional[float] = None,
    min_prominence: Optional[float] = None,
    horizontal_axis_units: float = 1,
) -> (np.ndarray, np.ndarray):
    """
    Identify peaks and estimate peak widths for a PXRD diffractogram.

    Arguments
    ---------
    intensity: diffractogram intensity data

    min_height: minimum intensity value required for a point to be considered a peak. When
        set to `None`, TODO

    min_prominence: minimum prominence required for a point to be considered a peak. When
        set to `None`, TODO

    Return value
    ------------
    peak_indices: indices of the `intensity` where peaks are located

    peak_widths: peaks widths

    Notes
    -----
    * The spacing of intensity values on the horizontal axis is assumed to be uniform.

    * See [scipy.signal.peak_prominences](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.peak_prominences.html) for details about peak prominences.

    """
    # --- Check arguments

    # min_height
    if min_height is None:
        min_height = np.quantile(intensity, q=_MIN_HEIGHT_QUANTILE)

    if min_height <= 0:
        raise ValueError(
            f"Invalid 'min_height' value: {min_height}. 'min_height' should be positive."
        )

    # min_prominence
    if min_prominence is None:
        min_prominence = np.quantile(intensity, q=_MIN_PROMINENCE_QUANTILE)

    if min_prominence <= 0:
        raise ValueError(
            f"Invalid 'min_prominence' value: {min_prominence}. 'min_prominence' should "
            "be positive."
        )

    # --- Find peaks

    # Identify peaks
    peak_indices, properties = scipy.signal.find_peaks(
        intensity, height=min_height, prominence=min_prominence
    )

    # Compute peak widths
    widths, _, _, _ = scipy.signal.peak_widths(intensity, peak_indices)
    peak_widths = horizontal_axis_units * widths

    return peak_indices, peak_widths
