"""
Unit tests for `pxrd_tools.analyze` module
"""
# --- Imports

# Standard library
import copy
import os
import unittest

# External packages
import numpy as np
import pytest

# Local packages/modules
import pxrd_tools.analyze
import pxrd_tools.io


# --- Test Suites


class test_pxrd_tools_analyze(unittest.TestCase):
    """
    Test suite for the `pxrd_tools.analyze` module
    """

    # --- Fixtures

    def setUp(self):
        """
        Prepare for test.
        """
        self.test_pxrd_data_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "data", "zircon.prn")
        )

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
        two_theta_valid = np.linspace(1, 2)
        intensity_valid = np.linspace(1, 10)

        # --- Exercise functionality and check results

        # ------ two_theta

        # intensity is not a NumPy array
        try:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                two_theta_valid.tolist(), intensity_valid, filter_window_size=None
            )
            assert True
        except Exception:
            pytest.fail("`intensity` as a list raised error")

        # two_theta is not a 1D vector
        two_theta_test = np.array([[1, 2], [4, 4]])

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                two_theta_test, intensity_valid
            )

        assert "two_theta' should be a 1D vector" in str(exception_info)

        # two_theta is empty
        two_theta_test = np.array([])

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                two_theta_test, intensity_valid
            )

        assert "'two_theta' should not be empty" in str(exception_info)

        # ------ intensity

        # intensity is not a NumPy array
        try:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                two_theta_valid, intensity_valid.tolist(), filter_window_size=None
            )
            assert True
        except Exception:
            pytest.fail("`intensity` as a list raised error")

        # intensity is not a 1D vector
        intensity_test = np.array([[1, 2], [4, 4]])

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                two_theta_valid, intensity_test
            )

        assert "'intensity' should be a 1D vector" in str(exception_info)

        # intensity is empty
        intensity_test = np.array([])

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                two_theta_valid, intensity_test
            )

        assert "'intensity' should not be empty" in str(exception_info)

        # ------ two_theta and intensity not the same size

        intensity_test = np.append(two_theta_valid, 0)

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                two_theta_valid, intensity_test
            )

        assert "'two_theta' and 'intensity' should be the same size" in str(
            exception_info
        )

        # ------ filter_order

        # filter_order = 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                two_theta_valid, intensity_valid, filter_order=0
            )

        assert "'filter_order' should be positive" in str(exception_info)

        # filter_order < 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                two_theta_valid, intensity_valid, filter_order=-5
            )

        assert "'filter_order' should be positive" in str(exception_info)

        # ------ filter_window_size

        # filter_window_size = 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                two_theta_valid, intensity_valid, filter_window_size=0
            )

        assert "'filter_window_size' should be positive" in str(exception_info)

        # filter_window_size < 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                two_theta_valid, intensity_valid, filter_window_size=-5
            )

        assert "'filter_window_size' should be positive" in str(exception_info)

        # filter_window_size = None
        try:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                two_theta_valid, intensity_valid, filter_window_size=None
            )
            assert True
        except Exception:
            pytest.fail(
                "`filter_window_size` set to `None` with valid `two_theta` and "
                "`intensity` raised error"
            )

        # ------ zhang_fit_repetitions

        # zhang_fit_repetitions = 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                two_theta_valid, intensity_valid, zhang_fit_repetitions=0
            )

        assert "'zhang_fit_repetitions' should be positive" in str(exception_info)

        # zhang_fit_repetitions < 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                two_theta_valid, intensity_valid, zhang_fit_repetitions=-5
            )

        assert "'zhang_fit_repetitions' should be positive" in str(exception_info)

        # ------ length of data less than filter_window

        intensity_test = [1, 2, 3, 4, 5]
        two_theta_test = [1, 2, 3, 4, 5]

        filter_window_size = 10

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.apply_diffractogram_corrections(
                two_theta_test, intensity_test, filter_window_size=filter_window_size
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
        intensity_no_noise = np.array([10, 20, 1.5, 5, 2, 9, 99, 25, 47])
        two_theta_no_noise = np.linspace(1, 1.5, num=len(intensity_no_noise))

        # Exercise functionality
        corrected_intensity_no_noise = (
            pxrd_tools.analyze.apply_diffractogram_corrections(
                two_theta_no_noise, intensity_no_noise
            )
        )

        # Check results
        assert isinstance(corrected_intensity_no_noise, np.ndarray)
        assert len(corrected_intensity_no_noise) == len(intensity_no_noise)

        # --- Test noise removal

        # Preparations
        rng = np.random.default_rng(seed=0)
        intensity_with_noise = copy.deepcopy(intensity_no_noise)
        intensity_with_noise += 0.05 * rng.standard_normal(len(intensity_no_noise))

        # Exercise functionality
        corrected_intensity_with_noise = (
            pxrd_tools.analyze.apply_diffractogram_corrections(
                two_theta_no_noise, intensity_no_noise
            )
        )

        # Check results
        assert isinstance(corrected_intensity_with_noise, np.ndarray)
        assert len(corrected_intensity_with_noise) == len(intensity_with_noise)
        np.testing.assert_allclose(
            corrected_intensity_with_noise,
            corrected_intensity_no_noise,
            rtol=0.1,
        )

    @staticmethod
    def test_find_peaks_arg_checks():
        """
        Test argument checks for `find_peaks()`.
        """
        # --- Preparations

        # valid data
        two_theta_valid = np.linspace(1, 2)
        intensity_valid = np.linspace(1, 10)

        # --- Exercise functionality and check results

        # ------ two_theta

        # two_theta is not a NumPy array
        try:
            pxrd_tools.analyze.find_peaks(
                two_theta_valid.tolist(),
                intensity_valid,
            )
            assert True
        except Exception:
            pytest.fail("`two_theta` as a list raised error")

        # two_theta is not a 1D vector
        two_theta_test = np.array([[1, 2], [4, 4]])

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_peaks(two_theta_test, intensity_valid)

        assert "two_theta' should be a 1D vector" in str(exception_info)

        # two_theta is empty
        two_theta_test = np.array([])

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_peaks(two_theta_test, intensity_valid)

        assert "'two_theta' should not be empty" in str(exception_info)

        # ------ intensity

        # intensity is not a NumPy array
        try:
            pxrd_tools.analyze.find_peaks(
                two_theta_valid,
                intensity_valid.tolist(),
            )
            assert True
        except Exception:
            pytest.fail("`intensity` as a list raised error")

        # intensity is not a 1D vector
        intensity_test = np.array([[1, 2], [4, 4]])

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_peaks(two_theta_valid, intensity_test)

        assert "'intensity' should be a 1D vector" in str(exception_info)

        # intensity is empty
        intensity_test = np.array([])

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_peaks(two_theta_valid, intensity_test)

        assert "'intensity' should not be empty" in str(exception_info)

        # ------ two_theta and intensity not the same size

        intensity_test = np.append(two_theta_valid, 0)

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_peaks(two_theta_valid, intensity_test)

        assert "'two_theta' and 'intensity' should be the same size" in str(
            exception_info
        )

        # ------ min_intensity_quantile

        # min_intensity_quantile < 0
        min_intensity_quantile = -1
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_peaks(
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
            pxrd_tools.analyze.find_peaks(
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
            pxrd_tools.analyze.find_peaks(two_theta_valid, intensity_valid, min_width=0)

        assert "'min_width' should be positive" in str(exception_info)

        # min_width < 0
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_peaks(
                two_theta_valid, intensity_valid, min_width=-5
            )

        assert "'min_width' should be positive" in str(exception_info)

        # ------ min_prominence_quantile

        # min_prominence_quantile < 0
        min_prominence_quantile = -1
        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.find_peaks(
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
            pxrd_tools.analyze.find_peaks(
                two_theta_valid,
                intensity_valid,
                min_prominence_quantile=min_prominence_quantile,
            )

        assert (
            f"Invalid 'min_prominence_quantile' value: {min_prominence_quantile}. "
            "'min_prominence_quantile' should lie in the interval [0, 1]."
            in str(exception_info)
        )

    def test_find_peaks(self):
        """
        Test `find_peaks()`.
        """
        # --- Preparations

        pxrd_data = pxrd_tools.io.read_csv(self.test_pxrd_data_file, delimiter=r"\s+")
        two_theta = pxrd_data["2-theta"].to_numpy()
        intensity = pxrd_data["count"].to_numpy()

        # Apply data corrections
        corrected_intensity = pxrd_tools.analyze.apply_diffractogram_corrections(
            two_theta, intensity
        )

        # --- Exercise functionality

        peaks, peak_widths, peak_indices = pxrd_tools.analyze.find_peaks(
            two_theta, corrected_intensity
        )

        # --- Check results

        # peak locations
        assert len(peaks) == 52
        assert np.all(peaks == two_theta[peak_indices])

        # peak widths
        assert len(peak_widths) == 52
        assert np.all(peak_widths >= pxrd_tools.analyze._MIN_PEAK_WIDTH_TWO_THETA)

        # peak indices
        assert len(peak_indices) == 52
        assert list(peak_indices) == [
            749,
            1099,
            1440,
            1529,
            1677,
            1782,
            1939,
            2128,
            2358,
            2422,
            2530,
            2735,
            2846,
            2893,
            3140,
            3149,
            3188,
            3416,
            3425,
            3519,
            3556,
            3788,
            3800,
            3878,
            3890,
            4149,
            4189,
            4203,
            4362,
            4414,
            4428,
            4462,
            4476,
            4502,
            4518,
            4956,
            4995,
            5431,
            5453,
            5474,
            5496,
            5630,
            5667,
            5726,
            5750,
            5782,
            5804,
            6155,
            6183,
            6513,
            6547,
            7163,
        ]
