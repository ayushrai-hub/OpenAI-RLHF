import unittest
from ideal_completion import (
    generate_table_images,
    calculate_swing_ratio,
    calculate_connection_ratio,
)
import os
import pandas as pd
class TestIdealCompletion(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for output
        self.test_dir = "test_output"
        os.makedirs(self.test_dir, exist_ok=True)

        # Create a sample metrics_df DataFrame
        self.metrics_df = pd.DataFrame({
            'Player': ['John Doe', 'Jane_Smith', "Mike ONeil", 'Anna-Marie Johnson'],
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
            'PitchTypeMetrics': [[], [], [], []]  # Simplified for testing
        })

    def tearDown(self):
        # Remove the temporary directory and its contents
        import shutil
        shutil.rmtree(self.test_dir)

    def test_basic_table_generation(self):
        # Generate table images
        generate_table_images(self.metrics_df, self.test_dir)

        # Get the list of generated files
        files = os.listdir(self.test_dir)

        # Check that filenames do not contain underscores and have correct format
        expected_filenames = [
            'JohnDoetable.png',
            'JaneSmithtable.png',
            'MikeONeiltable.png',
            'Anna-MarieJohnsontable.png'
        ]
        self.assertEqual(sorted(files), sorted(expected_filenames))

        # Ensure that no filename contains an underscore
        for filename in files:
            self.assertNotIn('_', filename)
            self.assertTrue(filename.endswith('table.png'))

    def test_calculate_swing_ratio(self):
        # Test with known data
        df = pd.DataFrame({
            'Call': ['Foul', 'Hit', 'Missed', 'BallCalled', 'StrikeCalled']
        })
        result = calculate_swing_ratio(df)
        expected_ratio = (3 / 5) * 100  # Three swings out of five pitches
        self.assertAlmostEqual(result, expected_ratio)

    def test_calculate_connection_ratio(self):
        df = pd.DataFrame({
            'Call': ['Foul', 'Hit', 'Missed', 'FoulNotPlayable', 'BallCalled']
        })
        result = calculate_connection_ratio(df)
        total_swings = 4  # Excluding 'BallCalled'
        total_contacts = 3  # Excluding 'Missed'
        expected_ratio = (total_contacts / total_swings) * 100
        self.assertAlmostEqual(result, expected_ratio)

    # Data Validation Edge Cases
    def test_data_validation_edge_cases(self):
        # Empty DataFrame
        empty_df = pd.DataFrame()
        try:
            generate_table_images(empty_df, self.test_dir)
            self.fail("Expected ValueError for empty DataFrame")
        except (ValueError, KeyError):
            pass  # Accept either ValueError or KeyError for empty DataFrame

        # Missing Required Columns
        incomplete_df = self.metrics_df.drop(['Swing%', 'Contact%'], axis=1)
        with self.assertRaises((KeyError, ValueError)):
            generate_table_images(incomplete_df, self.test_dir)

        # Invalid Data Types
        invalid_df = self.metrics_df.copy()
        invalid_df['Swing%'] = 'invalid'
        with self.assertRaises((TypeError, ValueError)):
            generate_table_images(invalid_df, self.test_dir)

        # NaN/Null Values
        nan_df = self.metrics_df.copy()
        nan_df.loc[0, 'Swing%'] = None
        with self.assertRaises((ValueError, TypeError)):
            generate_table_images(nan_df, self.test_dir)

        # Extreme Values
        extreme_df = self.metrics_df.copy()
        extreme_df.loc[0, 'Swing%'] = float('inf')
        with self.assertRaises((ValueError, TypeError)):
            generate_table_images(extreme_df, self.test_dir)

    # Ratio Calculation Edge Cases
    def test_ratio_calculation_edge_cases(self):
        # Empty Dataset
        empty_df = pd.DataFrame({'Call': []})
        self.assertEqual(calculate_swing_ratio(empty_df), 0)
        self.assertEqual(calculate_connection_ratio(empty_df), 0)

        # All Zeros Scenario
        zeros_df = pd.DataFrame({'Call': ['BallCalled'] * 5})
        self.assertEqual(calculate_swing_ratio(zeros_df), 0)
        self.assertEqual(calculate_connection_ratio(zeros_df), 0)

        # Invalid Call Types
        invalid_df = pd.DataFrame({'Call': ['Invalid', 'Unknown']})
        self.assertEqual(calculate_swing_ratio(invalid_df), 0)
        self.assertEqual(calculate_connection_ratio(invalid_df), 0)

        # Maximum Values
        all_swings_df = pd.DataFrame({'Call': ['Hit'] * 5})
        self.assertEqual(calculate_swing_ratio(all_swings_df), 100)
        self.assertEqual(calculate_connection_ratio(all_swings_df), 100)

    # File System Testing
    def test_file_system_scenarios(self):
        # Directory Permissions
        import stat
        os.chmod(self.test_dir, stat.S_IREAD)
        with self.assertRaises(PermissionError):
            generate_table_images(self.metrics_df, self.test_dir)
        os.chmod(self.test_dir, stat.S_IRWXU)  # Restore permissions

        # Existing File Handling
        with open(os.path.join(self.test_dir, 'JohnDoetable.png'), 'w') as f:
            f.write('existing file')
        generate_table_images(self.metrics_df, self.test_dir)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'JohnDoetable.png')))

        # Invalid Directory Path
        with self.assertRaises(OSError):
            generate_table_images(self.metrics_df, '/nonexistent/directory')

        # Unicode Paths
        unicode_dir = os.path.join(self.test_dir, 'テスト')
        os.makedirs(unicode_dir, exist_ok=True)
        generate_table_images(self.metrics_df, unicode_dir)
        self.assertTrue(os.path.exists(unicode_dir))

    # Player Name Sanitization Testing
    def test_player_name_sanitization_scenarios(self):
        # Empty Player Names
        empty_name_df = self.metrics_df.copy()
        empty_name_df.loc[0, 'Player'] = ''
        generate_table_images(empty_name_df, self.test_dir)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'table.png')))

        # Special Characters
        special_chars_df = self.metrics_df.copy()
        special_chars_df.loc[0, 'Player'] = 'Player#$%@'
        generate_table_images(special_chars_df, self.test_dir)
        sanitized_name = 'Player'  # All special chars should be removed
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, f'{sanitized_name}table.png')))

        # Long Player Names
        long_name_df = self.metrics_df.copy()
        long_name = 'A' * 50
        long_name_df.loc[0, 'Player'] = long_name
        generate_table_images(long_name_df, self.test_dir)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, f'{long_name}table.png')))

    # PitchTypeMetrics Testing
    def test_pitch_type_metrics_scenarios(self):
        # Valid Pitch Metrics
        pitch_df = self.metrics_df.copy()
        pitch_df.loc[0, 'PitchTypeMetrics'] = [
            {
                'Pitch Type': 'Fastball',
                'Swing%': 60.0,
                'Contact%': 80.0,
                'Miss%': 20.0,
                'Zone Contact%': 85.0,
                'Outside Swing%': 30.0
            }
        ]
        generate_table_images(pitch_df, self.test_dir)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'JohnDoetable.png')))

        # Invalid Pitch Metrics
        invalid_pitch_df = self.metrics_df.copy()
        invalid_pitch_df.loc[0, 'PitchTypeMetrics'] = [{'Invalid': 'Data'}]
        with self.assertRaises(KeyError):
            generate_table_images(invalid_pitch_df, self.test_dir)


if __name__ == "__main__":
    unittest.main(verbosity=2)
