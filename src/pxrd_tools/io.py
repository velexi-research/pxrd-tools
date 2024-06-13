"""
Data loading functions
"""

# --- Imports

# Standard library
import os
from pathlib import Path
import typing

# External packages
import pandas as pd
from pandas import DataFrame


# --- Constants

_PXRD_DATAFRAME_COLUMNS = ["2-theta", "count"]

# --- Functions


def read_csv(
    path: typing.Union[str, Path], delimiter: typing.Optional[str] = None
) -> DataFrame:
    """
    Read powder X-ray diffractogram from an ASCII file containing two columns: 2-theta
    and count.

    Parameters
    ----------
    path: path to data file

    delimiter: path to data file. Note: use a raw string when setting `delimiter` to a
    regular expression.

    Return value
    ------------
    DataFrame containing powder X-ray diffractogram
    """
    # --- Check arguments

    # Check that `path` exists
    if not os.path.isfile(path):
        raise ValueError(f"Data file '{path}' not found.")

    # Ensure that path is str
    path = str(path)

    # --- Load data from file

    # Load data set from file
    diffractogram = pd.read_csv(
        path,
        header=None,
        delimiter=delimiter,
        names=_PXRD_DATAFRAME_COLUMNS,
        index_col=False,
    )

    return diffractogram


def read_prn(path: typing.Union[str, Path]) -> DataFrame:
    """
    Read powder X-ray diffractogram from an PRN file. PRN files are space-separated data
    files containing two columns (2-theta and count) with leading whitespace.

    Parameters
    ----------
    path: path to data file

    Return value
    ------------
    DataFrame containing powder X-ray diffractogram
    """
    return read_csv(path, delimiter=r"\s+")
