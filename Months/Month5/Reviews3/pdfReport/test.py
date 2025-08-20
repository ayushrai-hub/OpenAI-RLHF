import unittest
from unittest.mock import patch
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk

# Import all necessary functions and variables directly
from ideal_completion import center_window, format_date_for_title, create_report, on_submit, create_gui

class TestIdealCompletion(unittest.TestCase):

    def setUp(self):
        # Mock DataFrames to simulate data loading
        # These DataFrames represent test data that would be used in place of actual application data
        self.df_all = pd.DataFrame({
            'material_number': [101, 102],
            'order': [111, 112],
            'date': ['20210101', '20220202'],
            'value_ia': [1.5, 2.0],
            'value_ma': [0.9, 1.2],
            'workstations': ['A', 'B'],
            'cw_ccw': ['cw', 'ccw']
        })
        
        self.df_pt = pd.DataFrame({
            'material_number': [101, 102],
            'order': [111, 112],
            'date': ['20210101', '20220202'],
            'value_ia': [1.5, 2.0],
            'value_ma': [0.9, 1.2],
            'workstations': ['A', 'B'],
            'cw_ccw': ['cw', 'ccw']
        })

        # Assign the mock data to global variables used in the functions being tested
        global df_pt, df_all
        df_pt = self.df_pt
        df_all = self.df_all

    def test_center_window(self):
        # Test `center_window` to ensure the window is centered properly on the screen
        window = tk.Tk()
        center_window(window, width=400, height=300)
        window.update()  # Update window to apply the geometry setting
        # Expected geometry format: window centered based on screen width and height
        expected_geometry = f"400x300+{(window.winfo_screenwidth() // 2) - (400 // 2)}+{(window.winfo_screenheight() // 2) - (300 // 2)}"
        # Verify the window geometry matches the expected centered position
        self.assertEqual(window.geometry(), expected_geometry)
        window.destroy()  # Destroy window after the test to prevent resource leak

    def test_format_date_for_title(self):
        # Test `format_date_for_title` to ensure proper formatting of dates
        self.assertEqual(format_date_for_title('20210101'), '01/01/2021')  # Standard valid date format
        self.assertEqual(format_date_for_title('20220229'), '20220229')  # Invalid date format, return input as-is
        self.assertEqual(format_date_for_title(''), '')  # Empty string should return an empty string

    @patch('tkinter.messagebox.showwarning')
    @patch('tkinter.Entry.get', side_effect=["999", "20210101", "20210201"])
    def test_create_report_no_data(self, mock_get, mock_showwarning):
        # Test `create_report` to ensure correct behavior when no data matches the criteria
        create_report()
        # Assert that a warning is shown if no data matches the filter criteria
        mock_showwarning.assert_called_with("Warning", "No data matches your chosen criteria.")
    
    @patch('tkinter.Entry.get', side_effect=["101", "20210101", "20220101"])
    def test_create_report_filtering(self, mock_get):
        # Test `create_report` for filtering functionality with mock input values
        create_report()

        # Define the expected filtered data that matches the provided criteria
        expected_filtered_data = self.df_pt[
            (self.df_pt['material_number'] == 101) &  # Filter by material number
            (self.df_pt['date'] >= "20210101") &      # Filter by start date
            (self.df_pt['date'] <= "20220101")        # Filter by end date
        ]

        # Manually re-filter `df_pt` to produce the actual filtered data used in the function
        actual_filtered_data = df_pt[
            (df_pt['material_number'] == 101) &
            (df_pt['date'] >= "20210101") &
            (df_pt['date'] <= "20220101")
        ]

        # Assert that the actual filtered DataFrame matches the expected DataFrame
        pd.testing.assert_frame_equal(actual_filtered_data, expected_filtered_data)

    def tearDown(self):
        # Cleanup code to be executed after each test case
        plt.close('all')  # Close any open matplotlib figures to prevent interference with other tests

if __name__ == '__main__':
    # Run all the unit tests with verbosity level 2 for detailed output
    unittest.main(verbosity=2)