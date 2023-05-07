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

        # valid data
        data_valid = DataFrame()
        data_valid["intensity"] = np.linspace(1, 10)
        data_valid["2-theta"] = np.linspace(1, 2)

        # --- Exercise functionality and check results

        # ------ data

        # data is empty
        data_test = DataFrame()

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(data_test)

        assert "'data' should not be empty" in str(exception_info)

        # data has a "two-theta" column instead of a "2-theta" column
        data_test = copy.deepcopy(data_valid)
        data_test.rename(columns={"2-theta": "two-theta"}, inplace=True)

        try:
            pxrd_tools.analyze.apply_diffractogram_corrections(data_test)
            assert True
        except Exception:
            pytest.fail("Valid `data` raised error")

        # data is does not have a "2-theta" or "two-theta" column
        data_test = copy.deepcopy(data_valid)
        del data_test["2-theta"]

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(data_test)

        assert "'data' should contain a '2-theta' or 'two-theta' column" in str(
            exception_info
        )

        # data has a "count" column instead of an "intensity" column
        data_test = copy.deepcopy(data_valid)
        data_test.rename(columns={"intensity": "count"}, inplace=True)

        try:
            pxrd_tools.analyze.apply_diffractogram_corrections(data_test)
            assert True
        except Exception:
            pytest.fail("Valid `data` raised error")

        # data is does not have an "intensity" or "count" column
        data_test = copy.deepcopy(data_valid)
        del data_test["intensity"]

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(data_test)

        assert "'data' should contain an 'intensity' or 'count' column" in str(
            exception_info
        )

        # ------ filter_order

        # filter_order = 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                data_valid, filter_order=0
            )

        assert "'filter_order' should be positive" in str(exception_info)

        # filter_order < 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                data_valid, filter_order=-5
            )

        assert "'filter_order' should be positive" in str(exception_info)

        # ------ filter_window_size

        # filter_window_size = 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                data_valid, filter_window_size=0
            )

        assert "'filter_window_size' should be positive" in str(exception_info)

        # filter_window_size < 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                data_valid, filter_window_size=-5
            )

        assert "'filter_window_size' should be positive" in str(exception_info)

        # filter_window_size = None
        data_test = copy.deepcopy(data_valid)
        data_test.rename(columns={"intensity": "count"}, inplace=True)

        try:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                data_test, filter_window_size=None
            )
            assert True
        except Exception:
            pytest.fail(
                "`filter_window_size` set to `None` with valid `data` raised error"
            )

        # ------ zhang_fit_repetitions

        # zhang_fit_repetitions = 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                data_valid, zhang_fit_repetitions=0
            )

        assert "'zhang_fit_repetitions' should be positive" in str(exception_info)

        # zhang_fit_repetitions < 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                data_valid, zhang_fit_repetitions=-5
            )

        assert "'zhang_fit_repetitions' should be positive" in str(exception_info)

        # ------ length of data less than filter_window

        data_test = DataFrame()
        data_test["intensity"] = [1, 2, 3, 4, 5]
        data_test["2-theta"] = [1, 2, 3, 4, 5]

        filter_window_size = 10

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                data_test, filter_window_size=filter_window_size
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
        data_no_noise = DataFrame()
        data_no_noise["intensity"] = np.array([10, 20, 1.5, 5, 2, 9, 99, 25, 47])
        data_no_noise["2-theta"] = np.linspace(1, 1.5, num=len(data_no_noise.index))

        # Exerciser functionality
        corrected_data_no_noise = pxrd_tools.analyze.apply_diffractogram_corrections(
            data_no_noise
        )

        # Check results
        assert isinstance(corrected_data_no_noise, DataFrame)
        assert len(corrected_data_no_noise.index) == len(data_no_noise.index)

        # --- Test noise removal

        # Preparations
        rng = np.random.default_rng(seed=0)
        data_with_noise = copy.deepcopy(data_no_noise)
        data_with_noise["intensity"] += 0.05 * rng.standard_normal(
            len(data_no_noise.index)
        )

        # Exerciser functionality
        corrected_data_with_noise = pxrd_tools.analyze.apply_diffractogram_corrections(
            data_with_noise
        )

        # Check results
        assert isinstance(corrected_data_with_noise, DataFrame)
        assert len(corrected_data_with_noise.index) == len(data_with_noise.index)
        np.testing.assert_allclose(
            corrected_data_with_noise["intensity"],
            corrected_data_no_noise["intensity"],
            rtol=0.1,
        )

    @staticmethod
    def test_find_diffractogram_peaks_arg_checks():
        """
        Test argument checks for `find_diffractogram_peaks()`.
        """
        # --- Preparations

        # valid data
        two_theta_valid = np.linspace(1, 2)
        intensity_valid = np.linspace(1, 10)

        # --- Exercise functionality and check results

        # ------ two_theta

        # two_theta is not a 1D vector
        two_theta_test = np.array([[1, 2], [4, 4]])

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_diffractogram_peaks(two_theta_test, intensity_valid)

        assert "two_theta' should be a 1D vector" in str(exception_info)

        # two_theta is empty
        two_theta_test = np.array([])

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_diffractogram_peaks(two_theta_test, intensity_valid)

        assert "'two_theta' should not be empty" in str(exception_info)

        # ------ intensity

        # intensity is not a 1D vector
        intensity_test = np.array([[1, 2], [4, 4]])

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_diffractogram_peaks(two_theta_valid, intensity_test)

        assert "'intensity' should be a 1D vector" in str(exception_info)

        # intensity is empty
        intensity_test = np.array([])

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_diffractogram_peaks(two_theta_valid, intensity_test)

        assert "'intensity' should not be empty" in str(exception_info)

        # ------ two_theta and intensity not the same size

        intensity_test = np.append(two_theta_valid, 0)

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_diffractogram_peaks(two_theta_valid, intensity_test)

        assert "'two_theta' and 'intensity' should be the same size" in str(
            exception_info
        )

        # ------ min_intensity_quantile

        # min_intensity_quantile < 0
        min_intensity_quantile = -1
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_diffractogram_peaks(
                two_theta_valid,
                intensity_valid,
                min_intensity_quantile=min_intensity_quantile,
            )

        assert (
            f"Invalid 'min_intensity_quantile' value: {min_intensity_quantile}. "
            "'min_intensity_quantile' should lie in the interval [0, 1]."
            in str(exception_info)
        )

        # min_intensity_quantile > 1
        min_intensity_quantile = 2
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_diffractogram_peaks(
                two_theta_valid,
                intensity_valid,
                min_intensity_quantile=min_intensity_quantile,
            )

        assert (
            f"Invalid 'min_intensity_quantile' value: {min_intensity_quantile}. "
            "'min_intensity_quantile' should lie in the interval [0, 1]."
            in str(exception_info)
        )

        # ------ min_width

        # min_width = 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_diffractogram_peaks(
                two_theta_valid, intensity_valid, min_width=0
            )

        assert "'min_width' should be positive" in str(exception_info)

        # min_width < 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_diffractogram_peaks(
                two_theta_valid, intensity_valid, min_width=-5
            )

        assert "'min_width' should be positive" in str(exception_info)

        # ------ min_prominence_quantile

        # min_prominence_quantile < 0
        min_prominence_quantile = -1
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_diffractogram_peaks(
                two_theta_valid,
                intensity_valid,
                min_prominence_quantile=min_prominence_quantile,
            )

        assert (
            f"Invalid 'min_prominence_quantile' value: {min_prominence_quantile}. "
            "'min_prominence_quantile' should lie in the interval [0, 1]."
            in str(exception_info)
        )

        # min_prominence_quantile > 1
        min_prominence_quantile = 2
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_diffractogram_peaks(
                two_theta_valid,
                intensity_valid,
                min_prominence_quantile=min_prominence_quantile,
            )

        assert (
            f"Invalid 'min_prominence_quantile' value: {min_prominence_quantile}. "
            "'min_prominence_quantile' should lie in the interval [0, 1]."
            in str(exception_info)
        )
