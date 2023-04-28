"""
Unit tests for `pxrd_tools.analyze` module.
"""
# --- Imports

# Standard library
import unittest

# External packages
import numpy as np
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
    def test_clean_up_diffractogram_arg_checks():
        """
        Test argument checks for `clean_up_diffractogram()`.
        """
        # --- Exercise functionality and check results

        # raw_intensity is an empty array
        raw_intensity = np.array([])

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.clean_up_diffractogram(raw_intensity)

        assert "'raw_intensity' should not be empty" in str(exception_info)

        # raw_intensity is a multi-dimensional array
        raw_intensity = np.array([[1, 2, 3], [4, 5, 6]])

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.clean_up_diffractogram(raw_intensity)

        assert "'raw_intensity' should be a 1D vector" in str(exception_info)

        # length of raw_intensity less than sg_filter_window
        raw_intensity = np.array([1, 2, 3, 4, 5])
        sg_filter_window = 10

        with pytest.raises(ValueError) as exception_info:
            pxrd_tools.analyze.clean_up_diffractogram(raw_intensity, sg_filter_window)

        assert (
            "If mode is 'interp', window_length must be less than or equal to the "
            "size of x." in str(exception_info)
        )

    def test_clean_up_diffractogram(self):
        """
        Test `clean_up_diffractogram()`.
        """
        # --- Test baseline removal

        # Preparations
        raw_intensity_no_noise = np.array([10, 20, 1.5, 5, 2, 9, 99, 25, 47])

        # Exerciser functionality
        intensity_no_noise = pxrd_tools.analyze.clean_up_diffractogram(
            raw_intensity_no_noise
        )

        # Check results
        assert isinstance(intensity_no_noise, np.ndarray)
        assert len(intensity_no_noise) == len(raw_intensity_no_noise)

        # --- Test noise removal

        # Preparations
        rng = np.random.default_rng(seed=0)
        raw_intensity_with_noise = raw_intensity_no_noise + 0.05 * rng.standard_normal(
            len(raw_intensity_no_noise)
        )

        # Exerciser functionality
        intensity_with_noise = pxrd_tools.analyze.clean_up_diffractogram(
            raw_intensity_with_noise
        )

        # Check results
        assert isinstance(intensity_with_noise, np.ndarray)
        assert len(intensity_with_noise) == len(raw_intensity_with_noise)
        np.testing.assert_allclose(intensity_with_noise, intensity_no_noise, rtol=0.1)
