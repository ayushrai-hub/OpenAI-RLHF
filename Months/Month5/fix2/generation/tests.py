import unittest
import os
import shutil
import tempfile
import time
import pandas as pd
from pathlib import Path
from ideal_completion import (
    generate_table_images,
    calculate_swing_ratio,
    calculate_connection_ratio,
)

class TestIdealCompletion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # It creates a sample data that will be used across all tests.
        cls.metrics_df = pd.DataFrame({
            'Player': ['John Doe', 'Jane Doe', "Sarah Red", 'Robert Joseph'],
            'Swing%': [50.0, 60.0, 70.0, 80.0],
            '1ST%': [20.0, 30.0, 40.0, 50.0],
            'Contact%': [90.0, 85.0, 80.0, 75.0],
            'Miss%': [10.0, 15.0, 20.0, 25.0],
            'Zone Contact%': [95.0, 90.0, 85.0, 80.0],
            'Outside Swing%': [5.0, 10.0, 15.0, 20.0],
            'Max Speed': [100.0, 98.0, 97.0, 96.0],
            '90th Percentile Speed': [95.0, 93.0, 92.0, 91.0],
            'Average Speed': [90.0, 88.0, 87.0, 86.0],
            'Average Launch Angle': [15.0, 14.0, 13.0, 12.0],
            'PitchTypeMetrics': [[], [], [], []]
        })

    def setUp(self):
        # It create a temporary directory for each test.
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        # Clean up temporary files after each test.
        def remove_readonly(func, path, excinfo):
            # Handle read-only files on Windows
            os.chmod(path, 0o666)
            func(path)

        # Wait for any potential file handles to be released
        time.sleep(0.1)
        try:
            shutil.rmtree(self.test_dir, onerror=remove_readonly)
        except Exception as e:
            print(f"Warning: Failed to remove test directory: {e}")

    def test_basic_table_generation(self):
        # It tests basic functionality of table generation.
        generate_table_images(self.metrics_df, self.test_dir)
        
        # Get the list of generated files using Path for cross-platform compatibility
        files = [f.name for f in Path(self.test_dir).glob('*.png')]
        
        expected_filenames = [
            'JohnDoe.png',
            'JaneDoe.png',
            'SarahRed.png',
            'RobertJoseph.png'
        ]
        
        self.assertEqual(sorted(files), sorted(expected_filenames))
        
        # Verify file contents and accessibility
        for filename in files:
            filepath = Path(self.test_dir) / filename
            self.assertTrue(filepath.exists())
            self.assertTrue(filepath.stat().st_size > 0)
            self.assertNotIn('_', filename)

    def test_calculate_swing_ratio(self):
        # It tests swing ratio calculation with various scenarios.
        test_cases = [
            # Normal case
            (pd.DataFrame({'Call': ['Foul', 'Hit', 'Missed', 'BallCalled', 'StrikeCalled']}), 60.0),
            # Empty case
            (pd.DataFrame({'Call': []}), 0.0),
            # All swings
            (pd.DataFrame({'Call': ['Hit', 'Hit', 'Missed']}), 100.0),
            # No swings
            (pd.DataFrame({'Call': ['BallCalled', 'StrikeCalled']}), 0.0),
            # Mixed case with invalid calls
            (pd.DataFrame({'Call': ['Hit', 'Invalid', 'BallCalled', 'Missed']}), 50.0),
        ]
        
        for df, expected in test_cases:
            with self.subTest(df=df):
                result = calculate_swing_ratio(df)
                self.assertAlmostEqual(result, expected, places=1)

    def test_calculate_connection_ratio(self):
        # It tests connection ratio calculation with various scenarios.
        test_cases = [
            # Normal case
            (pd.DataFrame({'Call': ['Foul', 'Hit', 'Missed', 'FoulNotPlayable']}), 75.0),
            # Empty case
            (pd.DataFrame({'Call': []}), 0.0),
            # All connections
            (pd.DataFrame({'Call': ['Hit', 'Foul', 'FoulNotPlayable']}), 100.0),
            # No connections
            (pd.DataFrame({'Call': ['Missed', 'Missed']}), 0.0),
            # Mixed case with invalid calls
            (pd.DataFrame({'Call': ['Hit', 'Invalid', 'Missed', 'Foul']}), 66.67),
        ]
        
        for df, expected in test_cases:
            with self.subTest(df=df):
                result = calculate_connection_ratio(df)
                self.assertAlmostEqual(result, expected, places=1)

    def test_input_validation(self):
        # It tests various input validation scenarios"""
        # Test empty DataFrame
        with self.assertRaises((ValueError, KeyError)):
            generate_table_images(pd.DataFrame(), self.test_dir)
        
        # Test missing required columns
        invalid_df = self.metrics_df.drop(['Swing%', 'Contact%'], axis=1)
        with self.assertRaises((ValueError, KeyError)):
            generate_table_images(invalid_df, self.test_dir)
        
        # Test invalid data types
        invalid_type_df = self.metrics_df.copy()
        invalid_type_df['Swing%'] = 'invalid'
        with self.assertRaises((TypeError, ValueError)):
            generate_table_images(invalid_type_df, self.test_dir)

    def test_special_characters_handling(self):
        # It tests handling of special characters in player names.
        special_chars_df = pd.DataFrame({
            'Player': ['John#Doe', 'Jane/Doe', 'Sarah*Red', 'Robert<>Joseph'],
            'Swing%': [50.0] * 4,
            '1ST%': [20.0] * 4,
            'Contact%': [90.0] * 4,
            'Miss%': [10.0] * 4,
            'Zone Contact%': [95.0] * 4,
            'Outside Swing%': [5.0] * 4,
            'Max Speed': [100.0] * 4,
            '90th Percentile Speed': [95.0] * 4,
            'Average Speed': [90.0] * 4,
            'Average Launch Angle': [15.0] * 4,
            'PitchTypeMetrics': [[], [], [], []]
        })
        
        generate_table_images(special_chars_df, self.test_dir)
        
        expected_files = {
            'JohnDoe.png',
            'JaneDoe.png',
            'SarahRed.png',
            'RobertJoseph.png'
        }
        
        actual_files = set(os.listdir(self.test_dir))
        self.assertEqual(expected_files, actual_files)

    def test_path_handling(self):
        # It tests handling of different path formats.
        # Test with absolute path
        abs_path = os.path.abspath(self.test_dir)
        generate_table_images(self.metrics_df, abs_path)
        
        # Test with relative path
        rel_path = os.path.relpath(self.test_dir)
        generate_table_images(self.metrics_df, rel_path)
        
        # Test with Path object
        path_obj = Path(self.test_dir)
        generate_table_images(self.metrics_df, path_obj)
        
        # All should create the same files
        self.assertTrue(all(f.exists() for f in Path(self.test_dir).glob('*.png')))

    def test_error_conditions(self):
        # It tests various error conditions.
        # Test with invalid directory path (using a device path that can't be created)
        if os.name == 'nt':
            invalid_dir = r'\\?\nul\invalid'  # invalid Windows device path
        else:  # Unix-like systems
            invalid_dir = '/dev/null/invalid'  # invalid Unix device path
            
        with self.assertRaises((OSError, FileNotFoundError)):
            generate_table_images(self.metrics_df, invalid_dir)
        
        # Test with file as output path
        invalid_path = os.path.join(self.test_dir, 'file.txt')
        Path(invalid_path).touch()
        with self.assertRaises((OSError, NotADirectoryError, PermissionError)):
            generate_table_images(self.metrics_df, invalid_path)

if __name__ == '__main__':
    unittest.main(verbosity=2)