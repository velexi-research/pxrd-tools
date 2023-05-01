"""
Diffractogram analysis functions
"""
# --- Imports

# Standard library
import math
from typing import Optional

# External packages
from BaselineRemoval import BaselineRemoval
from pandas import DataFrame
import numpy as np
import scipy


# --- Constants

# Data cleaning parameters
_DEFAULT_FILTER_ORDER = 3
_DEFAULT_FILTER_WINDOW_SIZE_TWO_THETA = 0.2
_DEFAULT_ZHANG_FIT_REPETITIONS = 15

# Peak detection parameters
_MIN_HEIGHT_QUANTILE = 0.8
_MIN_PROMINENCE_QUANTILE = 0.6

# --- Functions


def apply_diffractogram_corrections(
    data: DataFrame,
    filter_order: int = _DEFAULT_FILTER_ORDER,
    filter_window_size: Optional[int] = None,
    zhang_fit_repetitions: int = _DEFAULT_ZHANG_FIT_REPETITIONS,
) -> DataFrame:
    """
    Apply corrections to diffractogram data.

    `apply_diffractogram_corrections()` performs the following corrections.
      * Noise removal using the Savitzky-Golay filter.
      * Baseline correction using the algorithm developed by Zhang, Chen, and Liang (2010).

    Parameters
    ----------
    `data`: diffractogram data. Required columns:
      * "2-theta" or "two-theta"
      * "intensity" or "count"

    `filter_order`: order of the polynomial to use for the Savitzky-Golay filter

    `filter_window_size`: width of the window to use for the Savitzky-Golay filter. By
        default, the window size is set to $\\lceil 0.2 / \\Delta(2\\theta) \\rceil$,
        where $\\Delta(2\\theta)$ is the spacing $2 \\theta$ values in `data`. This
        choice yields a filter window that covers $0.2$ units of $2 \\theta$ (regardless
        of the grid spacing in `data`).

    `zhang_fit_repetitions`: number of iterations to use for the baseline removal algorithm
        developed by Zhang, Chen, and Liang (2010).

    Return Value
    ------------
    corrected diffractogram

    Notes
    -----
    * Required column names are case-insensitive.
    * The spacing between intensity values is assumed to be uniform in $2 \\theta$.
    """
    # --- Check arguments
    #
    # Notes
    # -----
    # * Savitzky-Golay filter parameters are checked by scipy.signal.savgol_filter()

    # Check that data is not empty
    if len(data.index) == 0:
        raise ValueError("'data' should not be empty")

    # Check that data contains the required columns
    columns = [column.lower() for column in data.columns]

    if "2-theta" in columns:
        two_theta_column = "2-theta"
    elif "two-theta" in columns:
        two_theta_column = "two-theta"
    else:
        raise ValueError("'data' should contain a '2-theta' or 'two-theta' column")

    if "intensity" in columns:
        intensity_column = "intensity"
    elif "count" in columns:
        intensity_column = "count"
    else:
        raise ValueError("'data' should contain an 'intensity' or 'count' column")

    # Check that the Savitky-Golay filter order is positive
    if filter_order <= 0:
        raise ValueError("'filter_order' should be positive")

    # If needed, set default Savitky-Golay filter window size
    if filter_window_size is None:
        filter_window_size = math.ceil(
            _DEFAULT_FILTER_WINDOW_SIZE_TWO_THETA
            / (data[two_theta_column][1] - data[two_theta_column][0])
        )

    # Check that the Savitky-Golay filter window size is positive
    if filter_window_size is not None and filter_window_size <= 0:
        raise ValueError("'filter_window_size' should be positive")

    # Check that the number of Zhang filter repetitions is positive
    if zhang_fit_repetitions <= 0:
        raise ValueError("'zhang_fit_repetitions' should be positive")

    # --- Preparations

    # Get intensity data
    corrected_intensity = data[intensity_column].to_numpy()

    # --- Apply data correction

    # Apply Savitzky-Golay filter to remove high frequency noise
    corrected_intensity = scipy.signal.savgol_filter(
        corrected_intensity, filter_window_size, filter_order
    )

    # Remove baseline
    corrected_intensity = BaselineRemoval(corrected_intensity).ZhangFit(
        repitition=zhang_fit_repetitions
    )

    # --- Construct DataFrame with results

    corrected_data = DataFrame()
    corrected_data[two_theta_column] = data[two_theta_column]
    corrected_data[intensity_column] = corrected_intensity

    return corrected_data


def find_peaks(
    intensity: np.ndarray,
    min_height: Optional[float] = None,
    min_prominence: Optional[float] = None,
    horizontal_axis_units: float = 1,
) -> (np.ndarray, np.ndarray):
    """
    Identify peaks and estimate peak widths for a PXRD diffractogram.

    Parameters
    ----------
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
