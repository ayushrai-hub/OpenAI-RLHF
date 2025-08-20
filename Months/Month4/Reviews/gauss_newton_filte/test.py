import unittest
from unittest.mock import patch, ANY
from testableIC import test_damped_gauss_newton_filter_design
import numpy as np

class TestDampedGaussNewtonFilterDesign(unittest.TestCase):

    @patch('testableIC.butter')
    def test_butter_called(self, mock_butter):
        """
        Test if butter() is called during the test function.
        """
        # Mock butter's return value to avoid errors
        mock_butter.return_value = ([0.1, 0.2, 0.3], [1.0, -0.5, 0.25])
        test_damped_gauss_newton_filter_design()
        mock_butter.assert_called_once()

    @patch('testableIC.butter')
    def test_butter_called_with_args(self, mock_butter):
        """
        Test if butter() is called with the correct arguments.
        """
        # Mock butter's return value to avoid errors
        mock_butter.return_value = ([0.1, 0.2, 0.3], [1.0, -0.5, 0.25])
        test_damped_gauss_newton_filter_design()
        # Check if butter was called with these specific arguments
        mock_butter.assert_called_once_with(ANY, 0.25, btype='low', analog=False)

    @patch('testableIC.damped_gauss_newton_filter_design')
    def test_damped_gauss_newton_filter_design_called(self, mock_dgnfd):
        """
        Test if damped_gauss_newton_filter_design() is called during the test function.
        """
        # Mock damped_gauss_newton_filter_design's return value
        mock_dgnfd.return_value = ([0.1, 0.2, 0.3], [1.0, -0.5, 0.25])
        test_damped_gauss_newton_filter_design()
        mock_dgnfd.assert_called_once()

# Run the tests
if __name__ == "__main__":
    unittest.main(verbosity=2)
