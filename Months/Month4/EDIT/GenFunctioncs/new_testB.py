# test_ideal_completion.py

import unittest
import os
import shutil
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from PIL import Image
from ideal_completion import *

class TestIdealCompletion(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_output"
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Sample test data
        self.metrics_df = pd.DataFrame({
            'Player': ['Test Player'],
            'Swing%': [50.0],
            '1ST%': [20.0],
            'Contact%': [90.0],
            'Miss%': [10.0],
            'Zone Contact%': [95.0],
            'Outside Swing%': [5.0],
            'Max Speed': [100.0],
            '90th Percentile Speed': [95.0],
            'Average Speed': [90.0],
            'Average Launch Angle': [15.0],
            'PitchTypeMetrics': [[]]
        })

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_invalid_data_types(self):
        df_invalid = self.metrics_df.copy()
        df_invalid.at[0, 'Swing%'] = 'invalid'
        with self.assertRaises(ValueError):
            generate_table_images(df_invalid, self.test_dir)

    def test_nan_null_values(self):
        df_with_nans = self.metrics_df.copy()
        df_with_nans.at[0, 'Swing%'] = np.nan
        with self.assertRaises(ValueError):
            generate_table_images(df_with_nans, self.test_dir)

    def test_malformed_pitch_metrics(self):
        df_invalid = self.metrics_df.copy()
        df_invalid.at[0, 'PitchTypeMetrics'] = [{'invalid': 'data'}]
        with self.assertRaises(ValueError):
            generate_table_images(df_invalid, self.test_dir)

    def test_floating_point_precision(self):
        df = pd.DataFrame({
            'Call': ['Foul'] + ['BallCalled'] * 999
        })
        result = calculate_swing_ratio(df)
        self.assertAlmostEqual(result, 0.1, places=4)

    @patch('os.statvfs')
    def test_disk_full_scenario(self, mock_statvfs):
        mock_stat = MagicMock()
        mock_stat.f_frsize = 1
        mock_stat.f_bfree = 1
        mock_statvfs.return_value = mock_stat
        
        with self.assertRaises(OSError):
            generate_table_images(self.metrics_df, "/nonexistent/path")

    def test_pre_existing_files(self):
        generate_table_images(self.metrics_df, self.test_dir)
        # Second generation should overwrite without errors
        generate_table_images(self.metrics_df, self.test_dir)
        files = os.listdir(self.test_dir)
        self.assertEqual(len(files), 1)

    def test_table_formatting(self):
        generate_table_images(self.metrics_df, self.test_dir)
        
        for filename in os.listdir(self.test_dir):
            filepath = os.path.join(self.test_dir, filename)
            with Image.open(filepath) as img:
                self.assertGreaterEqual(img.size[0], 400)
                self.assertGreaterEqual(img.size[1], 600)
                self.assertIn(img.mode, ['RGB', 'RGBA'])

    @patch('matplotlib.pyplot.figure')
    def test_figure_dimensions(self, mock_figure):
        generate_table_images(self.metrics_df, self.test_dir)
        mock_figure.assert_called()

    def test_font_properties(self):
        with patch('matplotlib.table.Table.set_fontsize') as mock_set_fontsize:
            generate_table_images(self.metrics_df, self.test_dir)
            mock_set_fontsize.assert_called()

if __name__ == '__main__':
    unittest.main(verbosity=2)