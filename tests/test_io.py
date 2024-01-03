"""
Unit tests for `pxrd_tools.io` module
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
        self.test_data_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "data")
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

        path = os.path.join(self.test_data_dir, "test-data.csv")
        data = pxrd_tools.io.read_csv(path)

        # Check results
        assert isinstance(data, DataFrame)
        assert list(data.columns) == pxrd_tools.io._PXRD_DATAFRAME_COLUMNS
        assert len(data) == 7251
        assert data.isna().sum().sum() == 0

        # ------ path is a Path

        path = Path(os.path.join(self.test_data_dir, "test-data.csv"))
        assert isinstance(path, Path)
        data = pxrd_tools.io.read_csv(path)

        # Check results
        assert isinstance(data, DataFrame)
        assert list(data.columns) == pxrd_tools.io._PXRD_DATAFRAME_COLUMNS
        assert len(data) == 7251
        assert data.isna().sum().sum() == 0

    @staticmethod
    def test_read_prn_arg_checks():
        """
        Test argument checks for `read_prn()`.
        """
        # --- Exercise functionality and check results

        path = "invalid/path"

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.io.read_prn(path)

        assert f"Data file '{path}' not found" in str(exception_info)

    def test_read_prn(self):
        """
        Test `read_prn()`.
        """
        # --- Exercise functionality and check results

        # ------ path is a str

        path = os.path.join(self.test_data_dir, "test-data.prn")
        data = pxrd_tools.io.read_prn(path)

        # Check results
        assert isinstance(data, DataFrame)
        assert list(data.columns) == pxrd_tools.io._PXRD_DATAFRAME_COLUMNS
        assert len(data) == 7251
        assert data.isna().sum().sum() == 0

        # ------ path is a Path

        path = Path(os.path.join(self.test_data_dir, "test-data.prn"))
        assert isinstance(path, Path)
        data = pxrd_tools.io.read_prn(path)

        # Check results
        assert isinstance(data, DataFrame)
        assert list(data.columns) == pxrd_tools.io._PXRD_DATAFRAME_COLUMNS
        assert len(data) == 7251
        assert data.isna().sum().sum() == 0
