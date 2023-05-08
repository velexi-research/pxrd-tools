"""
Main CLI program for PXRD analysis.
"""
# --- Imports

# Standard library
import logging
import os
from pathlib import Path
from typing import Annotated

# External packages
import numpy as np
from rich.console import Console
import typer

# Local package
import pxrd_tools.analyze
import pxrd_tools.io


# --- Constants

# Command arguments and options
from .shared import DATA_FILE_ARG
from .shared import QUIET_OPTION, DEFAULT_QUIET_OPTION
from .shared import LOG_FILE_OPTION, DEFAULT_LOG_FILE
from .shared import LOG_RECORD_FORMAT

from pxrd_tools.analyze import (
    _MIN_INTENSITY_QUANTILE,
    _MIN_PEAK_WIDTH_TWO_THETA,
    _MIN_PROMINENCE_QUANTILE,
)

# Typer app
app = typer.Typer()

# Global app options
global_options = {}

# --- Main app


@app.callback()
def main(
    quiet: Annotated[bool, QUIET_OPTION] = DEFAULT_QUIET_OPTION,
    log_file: Annotated[Path, LOG_FILE_OPTION] = DEFAULT_LOG_FILE,
) -> None:
    """
    PXRD Tools
    """
    # Set global options
    global_options["quiet"] = quiet

    # Initialize logger
    logging.basicConfig(level=logging.INFO, filename=log_file, format=LOG_RECORD_FORMAT)


# --- Commands

# Command arguments and options
_VALID_INTENSITY_SCALE_OPTIONS = ["count", "sqrt", "log"]
_INTENSITY_SCALE_OPTION = typer.Option(
    "--intensity-scale",
    "-S",
    help=f"Intensity scale. Valid values: {_VALID_INTENSITY_SCALE_OPTIONS}",
)

_MIN_INTENSITY_QUANTILE_OPTION = typer.Option(
    "--min-intensity-quantile",
    "-Q",
    help="Quantile of the intensity to use for the minimum peak intensity.",
)

_MIN_PEAK_WIDTH_OPTION = typer.Option(
    "--min-peak-width",
    "-W",
    help="Minimum peak width (in units of 2-theta)",
)

_MIN_PROMINENCE_QUANTILE_OPTION = typer.Option(
    "--min-prominence-quantile",
    "-P",
    help=(
        "Quantile of the prominence to use as the minimum peak prominence. "
        "Note: the distribution of peak prominences is constructed from the "
        "peaks detected using only the `min-intensity-quantile` and `min-peak-width` "
        "parameters."
    ),
)


@app.command()
def peaks(
    data_file: Annotated[Path, DATA_FILE_ARG],
    intensity_scale: Annotated[str, _INTENSITY_SCALE_OPTION] = "sqrt",
    min_intensity_quantile: Annotated[
        float, _MIN_INTENSITY_QUANTILE_OPTION
    ] = _MIN_INTENSITY_QUANTILE,
    min_peak_width: Annotated[
        float, _MIN_PEAK_WIDTH_OPTION
    ] = _MIN_PEAK_WIDTH_TWO_THETA,
    min_prominence_quantile: Annotated[
        float, _MIN_PROMINENCE_QUANTILE_OPTION
    ] = _MIN_PROMINENCE_QUANTILE,
    quiet_local: Annotated[bool, QUIET_OPTION] = DEFAULT_QUIET_OPTION,
) -> None:
    """
    Identify peaks in PXRD data contained in `data_file`.
    """
    # --- Create error console

    error_console = Console(stderr=True)

    # --- Check arguments

    # Ensure that intensity_scale is lowercase
    intensity_scale = intensity_scale.lower()

    if intensity_scale not in _VALID_INTENSITY_SCALE_OPTIONS:
        message = (
            f"'{intensity_scale}' is not a valid intensity scale. "
            f"Valid values: {_VALID_INTENSITY_SCALE_OPTIONS}"
        )
        error_console.print(message)
        raise typer.Abort()

    # --- Preparations

    # Set data file delimiter based on file extension
    _, ext = os.path.splitext(data_file)
    if ext == ".prn":
        delimiter = r"\s+"
    else:
        delimiter = None
    print(ext)

    # Load PXRD data
    data = pxrd_tools.io.read_csv(data_file, delimiter=delimiter)

    # Extract 2-theta and count data
    two_theta = data["2-theta"].to_numpy()
    intensity = data["count"].to_numpy()

    # --- Find PXRD peaks

    # Rescale intensity
    if intensity_scale == "sqrt":
        intensity = np.sqrt(intensity)
    elif intensity_scale == "log":
        intensity = np.log(intensity + 1)

    # Apply diffractogram corrections
    intensity = pxrd_tools.analyze.apply_diffractogram_corrections(two_theta, intensity)

    # Identify diffractogram peaks
    peaks, peak_widths, _ = pxrd_tools.analyze.find_peaks(
        two_theta,
        intensity,
        min_intensity_quantile=min_intensity_quantile,
        min_width=min_peak_width,
        min_prominence_quantile=min_prominence_quantile,
    )

    print(peaks)
