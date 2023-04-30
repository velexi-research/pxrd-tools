"""
Unit tests for `pxrd_tools.analyze` module.
"""
# --- Imports

# Standard library
import copy
import unittest

# External packages
import numpy as np
from pandas import DataFrame
import pytest

# Local modules
import pxrd_tools.analyze


# --- Test Suites


class test_pxrd_tools_analyze(unittest.TestCase):
    """
    Test suite for the `pxrd_tools.analyze` module.
    """

    # --- Fixtures

    def setUp(self):
        """
        Prepare for test.
        """

    def tearDown(self):
        """
        Clean up after test.
        """

    # --- Tests

    @staticmethod
    def test_apply_diffractogram_corrections_arg_checks():
        """
        Test argument checks for `apply_diffractogram_corrections()`.
        """
        # --- Preparations

        # valid raw_data
        raw_data_valid = DataFrame()
        raw_data_valid["intensity"] = np.linspace(1, 10)
        raw_data_valid["2-theta"] = np.linspace(1, 2)

        # --- Exercise functionality and check results

        # raw_data is empty
        raw_data_test = DataFrame()

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(raw_data_test)

        assert "'raw_data' should not be empty" in str(exception_info)

        # raw_data has a "two-theta" column instead of a "2-theta" column
        raw_data_test = copy.deepcopy(raw_data_valid)
        raw_data_test.rename(columns={"2-theta": "two-theta"}, inplace=True)

        try:
            pxrd_tools.analyze.apply_diffractogram_corrections(raw_data_test)
            assert True
        except Exception:
            pytest.fail("Valid `raw_data` raised error")

        # raw_data is does not have a "2-theta" or "two-theta" column
        raw_data_test = copy.deepcopy(raw_data_valid)
        del raw_data_test["2-theta"]

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(raw_data_test)

        assert "'raw_data' should contain a '2-theta' or 'two-theta' column" in str(
            exception_info
        )

        # raw_data has a "count" column instead of an "intensity" column
        raw_data_test = copy.deepcopy(raw_data_valid)
        raw_data_test.rename(columns={"intensity": "count"}, inplace=True)

        try:
            pxrd_tools.analyze.apply_diffractogram_corrections(raw_data_test)
            assert True
        except Exception:
            pytest.fail("Valid `raw_data` raised error")

        # raw_data is does not have an "intensity" or "count" column
        raw_data_test = copy.deepcopy(raw_data_valid)
        del raw_data_test["intensity"]

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(raw_data_test)

        assert "'raw_data' should contain an 'intensity' or 'count' column" in str(
            exception_info
        )

        # filter_order = 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                raw_data_valid, filter_order=0
            )

        assert "'filter_order' should be positive" in str(exception_info)

        # filter_order < 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                raw_data_valid, filter_order=-5
            )

        assert "'filter_order' should be positive" in str(exception_info)

        # filter_window_size = 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                raw_data_valid, filter_window_size=0
            )

        assert "'filter_window_size' should be positive" in str(exception_info)

        # filter_window_size < 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                raw_data_valid, filter_window_size=-5
            )

        assert "'filter_window_size' should be positive" in str(exception_info)

        # filter_window_size = None
        raw_data_test = copy.deepcopy(raw_data_valid)
        raw_data_test.rename(columns={"intensity": "count"}, inplace=True)

        try:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                raw_data_test, filter_window_size=None
            )
            assert True
        except Exception:
            pytest.fail(
                "`filter_window_size` set to `None` with valid `raw_data` raised error"
            )

        # zhang_fit_repetitions = 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                raw_data_valid, zhang_fit_repetitions=0
            )

        assert "'zhang_fit_repetitions' should be positive" in str(exception_info)

        # zhang_fit_repetitions < 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                raw_data_valid, zhang_fit_repetitions=-5
            )

        assert "'zhang_fit_repetitions' should be positive" in str(exception_info)

        # length of raw_data less than filter_window
        raw_data_test = DataFrame()
        raw_data_test["intensity"] = [1, 2, 3, 4, 5]
        raw_data_test["2-theta"] = [1, 2, 3, 4, 5]

        filter_window_size = 10

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                raw_data_test, filter_window_size=filter_window_size
            )

        assert (
            "If mode is 'interp', window_length must be less than or equal to the "
            "size of x." in str(exception_info)
        )

    @staticmethod
    def test_apply_diffractogram_corrections():
        """
        Test `apply_diffractogram_corrections()`.
        """
        # --- Test baseline removal

        # Preparations
        raw_data_no_noise = DataFrame()
        raw_data_no_noise["intensity"] = np.array([10, 20, 1.5, 5, 2, 9, 99, 25, 47])
        raw_data_no_noise["2-theta"] = np.linspace(
            1, 1.5, num=len(raw_data_no_noise.index)
        )

        # Exerciser functionality
        corrected_data_no_noise = pxrd_tools.analyze.apply_diffractogram_corrections(
            raw_data_no_noise
        )

        # Check results
        assert isinstance(corrected_data_no_noise, DataFrame)
        assert len(corrected_data_no_noise.index) == len(raw_data_no_noise.index)

        # --- Test noise removal

        # Preparations
        rng = np.random.default_rng(seed=0)
        raw_data_with_noise = copy.deepcopy(raw_data_no_noise)
        raw_data_with_noise["intensity"] += 0.05 * rng.standard_normal(
            len(raw_data_no_noise.index)
        )

        # Exerciser functionality
        corrected_data_with_noise = pxrd_tools.analyze.apply_diffractogram_corrections(
            raw_data_with_noise
        )

        # Check results
        assert isinstance(corrected_data_with_noise, DataFrame)
        assert len(corrected_data_with_noise.index) == len(raw_data_with_noise.index)
        np.testing.assert_allclose(
            corrected_data_with_noise["intensity"],
            corrected_data_no_noise["intensity"],
            rtol=0.1,
        )
