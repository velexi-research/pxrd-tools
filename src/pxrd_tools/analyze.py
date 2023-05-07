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


# --- Functions

# Data correction parameters
_DEFAULT_FILTER_ORDER = 3
_DEFAULT_FILTER_WINDOW_SIZE_TWO_THETA = 0.2
_DEFAULT_ZHANG_FIT_REPETITIONS = 15


# TODO: add parameters for 2-theta and intensity columns
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

    # --- Construct DataFrame containing corrected data

    corrected_data = DataFrame()
    corrected_data[two_theta_column] = data[two_theta_column]
    corrected_data[intensity_column] = corrected_intensity

    return corrected_data


# Peak detection parameters
_MIN_INTENSITY_QUANTILE = 0.75
_MIN_PEAK_WIDTH_TWO_THETA = 0.015
_MIN_PROMINENCE_QUANTILE = 0.25


def find_diffractogram_peaks(
    two_theta: np.ndarray,
    intensity: np.ndarray,
    min_intensity_quantile: float = _MIN_INTENSITY_QUANTILE,
    min_width: float = _MIN_PEAK_WIDTH_TWO_THETA,
    min_prominence_quantile: float = _MIN_PROMINENCE_QUANTILE,
) -> (np.ndarray, np.ndarray):
    """
    Find peaks and estimate peak widths for a PXRD diffractogram.

    Parameters
    ----------
    `two_theta`: 2-theta values

    `intensity`: intensity values

    `min_intensity_quantile`: quantile of the intensity to use as the minimum peak intensity

    `min_width`: minimum peak width in units of 2-theta

    `min_prominence_quantile`: quantile of the prominence to use as the minimum peak
        prominence. Note: the distribution of peak prominences is constructed from the
        peaks detected using only the `min_intensity_quantile` and `min_width` parameters.

    Return value
    ------------
    `peaks`: indicies of the intensity where peaks are located

    `peak_widths`: peak widths in units of 2-theta

    Notes
    -----
    * The spacing of 2-theta values is assumed to be uniform.

    * See [scipy.signal.peak_prominences](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.peak_prominences.html) for details about peak prominences.
    """
    # --- Check arguments

    # Check that two_theta is a vector
    if len(two_theta.shape) > 1 or np.prod(two_theta.shape) != two_theta.size:
        raise ValueError("'two_theta' should be a 1D vector")

    # Check that two_theta is not empty
    if len(two_theta) == 0:
        raise ValueError("'two_theta' should not be empty")

    # Check that intensity is a vector
    if len(intensity.shape) > 1 or np.prod(intensity.shape) != intensity.size:
        raise ValueError("'intensity' should be a 1D vector")

    # Check that intensity is not empty
    if len(intensity) == 0:
        raise ValueError("'intensity' should not be empty")

    # Check that two_theta and intensity have the same shape
    if intensity.size != two_theta.size:
        raise ValueError("'two_theta' and 'intensity' should be the same size")

    # min_intensity_quantile
    if min_intensity_quantile < 0 or min_intensity_quantile > 1:
        raise ValueError(
            f"Invalid 'min_intensity_quantile' value: {min_intensity_quantile}. "
            "'min_intensity_quantile' should lie in the interval [0, 1]."
        )

    # min_width
    if min_width <= 0:
        raise ValueError(
            f"Invalid 'min_width' value: {min_width}. 'min_width' should be positive."
        )

    # min_prominence_quantile
    if min_prominence_quantile < 0 or min_prominence_quantile > 1:
        raise ValueError(
            f"Invalid 'min_prominence_quantile' value: {min_prominence_quantile}. "
            "'min_prominence_quantile' should lie in the interval [0, 1]."
        )

    # --- Preparations

    # Compute spacing of 2-theta values
    delta_two_theta = two_theta[1] - two_theta[0]
    min_index_width = min_width / delta_two_theta

    # ------ Compute minimum intensity to use for finding peaks

    intensity_mean = np.mean(intensity)

    intensity_quantile = np.quantile(intensity, q=min_intensity_quantile)

    if intensity_mean > intensity_quantile:
        min_intensity = intensity_mean
    else:
        min_intensity = intensity_quantile

    # --- Find peaks

    # Find peaks without prominence constraint
    peaks, properties = scipy.signal.find_peaks(
        intensity, height=min_intensity, width=min_index_width
    )

    # Compute peak prominences
    peak_prominences, _, _ = scipy.signal.peak_prominences(intensity, peaks)

    # Compute minimim peak prominence
    min_prominence = np.quantile(peak_prominences, q=min_prominence_quantile)

    # Find peaks with height and prominence constraints
    peaks, properties = scipy.signal.find_peaks(
        intensity,
        height=min_intensity,
        width=min_index_width,
        prominence=min_prominence,
    )

    # --- Compute peak widths

    widths, _, _, _ = scipy.signal.peak_widths(intensity, peaks)
    peak_widths = delta_two_theta * widths

    return peaks, peak_widths
