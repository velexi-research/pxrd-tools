"""
Unit tests for `pxrd_tools.io` module.
"""
# --- Imports

# Standard library
import os
from pathlib import Path
import unittest

# External packages
from pandas import DataFrame
import pytest

# Local packages/modules
import pxrd_tools.io


# --- Test Suites


class test_pxrd_tools_io(unittest.TestCase):
    """
    Test suite for the `pxrd_tools.io` module.
    """

    # --- Fixtures

    def setUp(self):
        """
        Prepare for test.
        """
        self.test_data_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "data", "test-data.csv")
        )

    def tearDown(self):
        """
        Clean up after test.
        """

    # --- Tests

    @staticmethod
    def test_read_csv_arg_checks():
        """
        Test argument checks for `read_csv()`.
        """
        # --- Exercise functionality and check results

        path = "invalid/path"

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.io.read_csv(path)

        assert f"Data file '{path}' not found" in str(exception_info)

    def test_read_csv(self):
        """
        Test `read_csv()`.
        """
        # --- Exercise functionality and check results

        # ------ path is a str

        path = self.test_data_file
        data = pxrd_tools.io.read_csv(path, delimiter=r"\s+")

        # Check results
        assert isinstance(data, DataFrame)
        assert list(data.columns) == pxrd_tools.io._PXRD_DATAFRAME_COLUMNS
        assert len(data) == 7251

        # ------ path is a Path

        path = Path(self.test_data_file)
        assert isinstance(path, Path)
        data = pxrd_tools.io.read_csv(path, delimiter=r"\s+")

        # Check results
        assert isinstance(data, DataFrame)
        assert list(data.columns) == pxrd_tools.io._PXRD_DATAFRAME_COLUMNS
        assert len(data) == 7251
