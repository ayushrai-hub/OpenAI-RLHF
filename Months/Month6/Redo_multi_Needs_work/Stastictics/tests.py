import unittest
import os
import shutil
import tempfile
import time
import pandas as pd
import warnings
from pathlib import Path
from ideal_completion import (
    generate_table_images,
    calculate_swing_ratio,
    calculate_connection_ratio
)

class TestIdealCompletion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(self.cleanup_test_dir)
    
    def cleanup_test_dir(self):
        try:
            time.sleep(0.1)
            if os.path.exists(self.test_dir):
                def handle_error(func, path, exc_info):
                    os.chmod(path, 0o666)
                    func(path)
                shutil.rmtree(self.test_dir, onerror=handle_error)
        except Exception as e:
            print(f"Warning: Failed to remove test directory: {e}")

    def test_basic_table_generation(self):
        generate_table_images(self.metrics_df, self.test_dir)
        
        files = set(f.name for f in Path(self.test_dir).glob('*.png'))
        expected_files = {
            'JohnDoe.png',
            'JaneDoe.png',
            'SarahRed.png',
            'RobertJoseph.png'
        }
        
        self.assertEqual(files, expected_files)
        
        for filename in files:
            filepath = Path(self.test_dir) / filename
            self.assertTrue(filepath.exists())
            self.assertTrue(filepath.stat().st_size > 0)
            self.assertNotIn('_', filename)

    def test_calculate_swing_ratio(self):
        test_cases = [
            (pd.DataFrame({'Call': ['Foul', 'Hit', 'Missed', 'BallCalled', 'StrikeCalled']}), 60.0),
            (pd.DataFrame({'Call': []}), 0.0),
            (pd.DataFrame({'Call': ['Hit', 'Hit', 'Missed']}), 100.0),
            (pd.DataFrame({'Call': ['BallCalled', 'StrikeCalled']}), 0.0),
            (pd.DataFrame({'Call': ['Hit', 'Invalid', 'BallCalled', 'Missed']}), 50.0),
        ]
        
        for df, expected in test_cases:
            with self.subTest(df=df):
                result = calculate_swing_ratio(df)
                self.assertAlmostEqual(result, expected, places=1)

    def test_calculate_connection_ratio(self):
        test_cases = [
            (pd.DataFrame({'Call': ['Foul', 'Hit', 'Missed', 'FoulNotPlayable']}), 75.0),
            (pd.DataFrame({'Call': []}), 0.0),
            (pd.DataFrame({'Call': ['Hit', 'Foul', 'FoulNotPlayable']}), 100.0),
            (pd.DataFrame({'Call': ['Missed', 'Missed']}), 0.0),
            (pd.DataFrame({'Call': ['Hit', 'Invalid', 'Missed', 'Foul']}), 66.67),
        ]
        
        for df, expected in test_cases:
            with self.subTest(df=df):
                result = calculate_connection_ratio(df)
                self.assertAlmostEqual(result, expected, places=1)

    def test_input_validation(self):
        with self.assertRaises(ValueError):
            generate_table_images(pd.DataFrame(), self.test_dir)
        
        invalid_df = self.metrics_df.drop(['Swing%', 'Contact%'], axis=1)
        with self.assertRaises(ValueError):
            generate_table_images(invalid_df, self.test_dir)
        
        # Test invalid type with proper pandas type conversion
        invalid_type_df = self.metrics_df.copy()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            invalid_type_df = invalid_type_df.astype({'Swing%': 'object'})
            invalid_type_df.at[0, 'Swing%'] = 'invalid'
        
        with self.assertRaises(ValueError):
            generate_table_images(invalid_type_df, self.test_dir)

    def test_special_characters_handling(self):
        special_chars_df = self.metrics_df.copy()
        special_chars_df['Player'] = [
            'John-Doe#123',
            'Jane/Doe@456',
            'Sarah*Red&789',
            'Robert<>Joseph!'
        ]
        
        generate_table_images(special_chars_df, self.test_dir)
        
        expected_files = {
            'John-Doe123.png',
            'JaneDoe456.png',
            'SarahRed789.png',
            'RobertJoseph.png'
        }
        
        actual_files = set(os.listdir(self.test_dir))
        self.assertEqual(expected_files, actual_files)

    def test_path_handling(self):
        nested_dir = Path(self.test_dir) / "nested" / "path"
        nested_dir.mkdir(parents=True, exist_ok=True)
        
        paths_to_test = [
            str(nested_dir),
            nested_dir,
            nested_dir.resolve(),
        ]
        
        for path in paths_to_test:
            with self.subTest(path=path):
                generate_table_images(self.metrics_df, path)
                files = list(Path(path).glob('*.png'))
                self.assertEqual(len(files), 4)
                self.assertTrue(all(f.stat().st_size > 0 for f in files))


    def test_error_conditions(self):
        # Test with non-existent directory
        with tempfile.NamedTemporaryFile() as tmp_file:
            invalid_dir = Path(tmp_file.name) / "cannot_create"
            with self.assertRaises((OSError, PermissionError)):
                generate_table_images(self.metrics_df, invalid_dir)
        
        # Test with read-only directory in a cross-platform way
        readonly_dir = Path(self.test_dir) / "readonly"
        readonly_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Make directory read-only in a cross-platform way
            if os.name == 'nt':  # Windows
                try:
                    import win32api, win32con
                    win32api.SetFileAttributes(str(readonly_dir), win32con.FILE_ATTRIBUTE_READONLY)
                except ImportError:
                    # Fallback if pywin32 is not installed
                    os.chmod(readonly_dir, 0o444)
            else:  # Unix-like systems
                os.chmod(readonly_dir, 0o444)
            
            with self.assertRaises((OSError, PermissionError)):
                generate_table_images(self.metrics_df, readonly_dir)
        finally:
            # Restore permissions for cleanup
            try:
                if os.name == 'nt':
                    try:
                        import win32api, win32con
                        win32api.SetFileAttributes(str(readonly_dir), win32con.FILE_ATTRIBUTE_NORMAL)
                    except ImportError:
                        os.chmod(readonly_dir, 0o777)
                else:
                    os.chmod(readonly_dir, 0o777)
            except Exception:
                pass  # Ignore cleanup errors


if __name__ == '__main__':
    unittest.main(verbosity=2)