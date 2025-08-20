import unittest
from datetime import datetime, timedelta
import numpy as np
from typing import List, NamedTuple

# Import the function to be tested
from test_original import lowess_interpolation, Analysis, Blanks, RE_as_HB

class TestLowessInterpolation(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2024, 1, 1, 0, 0, 0)
        self.blanks = [
            Blanks(self.now + timedelta(hours=i), 1.0 + 0.1 * i, 0.05, True)
            for i in range(10)
        ]
        self.sequence_data = [
            Analysis(self.now + timedelta(hours=i+0.5), 1.5 + 0.2 * i, 0.1, f"Sample {i}", "unknown", True)
            for i in range(9)
        ]
        self.RE_as_HBs = []

    def test_basic_interpolation(self):
        results = lowess_interpolation(self.sequence_data, self.blanks, self.RE_as_HBs, smooth=True)
        self.assertEqual(len(results), 9)
        for result in results:
            self.assertIn('time', result)
            self.assertIn('interpolated_ratio', result)
            self.assertIn('interpolated_error', result)
            self.assertIn('hovlabel', result)

    def test_smooth_vs_not_smooth(self):
        smooth_results = lowess_interpolation(self.sequence_data, self.blanks, self.RE_as_HBs, smooth=True)
        not_smooth_results = lowess_interpolation(self.sequence_data, self.blanks, self.RE_as_HBs, smooth=False)
        self.assertNotEqual(
            [r['interpolated_ratio'] for r in smooth_results],
            [r['interpolated_ratio'] for r in not_smooth_results]
        )

    def test_empty_input(self):
        results = lowess_interpolation([], self.blanks, self.RE_as_HBs, smooth=True)
        self.assertEqual(len(results), 0)

    def test_all_inactive_analyses(self):
        inactive_sequence = [
            Analysis(self.now + timedelta(hours=i+0.5), 1.5 + 0.2 * i, 0.1, f"Sample {i}", "unknown", False)
            for i in range(9)
        ]
        results = lowess_interpolation(inactive_sequence, self.blanks, self.RE_as_HBs, smooth=True)
        self.assertEqual(len(results), 0)

    def test_non_unknown_analyses(self):
        mixed_sequence = self.sequence_data + [
            Analysis(self.now + timedelta(hours=10), 3.5, 0.1, "Non-unknown", "other", True)
        ]
        results = lowess_interpolation(mixed_sequence, self.blanks, self.RE_as_HBs, smooth=True)
        self.assertEqual(len(results), 9)  # Should still be 9, ignoring the non-unknown analysis

    def test_interpolation_boundaries(self):
        results = lowess_interpolation(self.sequence_data, self.blanks, self.RE_as_HBs, smooth=True)
        first_interp = results[0]['interpolated_ratio']
        last_interp = results[-1]['interpolated_ratio']
        self.assertGreater(last_interp, first_interp)  # Assuming increasing trend in blanks

    def test_hovlabel_format(self):
        results = lowess_interpolation(self.sequence_data, self.blanks, self.RE_as_HBs, smooth=True)
        for result in results:
            hovlabel = result['hovlabel']
            self.assertIn("Sample", hovlabel)
            self.assertIn("Ratio:", hovlabel)
            self.assertIn("Blank Correction:", hovlabel)

    def test_error_propagation(self):
        results = lowess_interpolation(self.sequence_data, self.blanks, self.RE_as_HBs, smooth=True)
        for result in results:
            self.assertGreater(result['interpolated_error'], 0)  # Error should be positive

if __name__ == '__main__':
    unittest.main(verbosity=2)