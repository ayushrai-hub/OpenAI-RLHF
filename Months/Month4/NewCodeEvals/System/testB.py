# ideal_unit_test.py
import unittest
import math
from ideal_completion import Storage

class StorageTestCase(unittest.TestCase):
    def test_successful_backup(self):
        """Test that backup is successful when duration <= 60 seconds."""
        storage = Storage(30, 1)  # duration = 30 / 1 = 30 seconds
        duration, success = storage.start_backup()
        self.assertEqual(duration, 30)
        self.assertTrue(success)

    def test_unsuccessful_backup(self):
        """Test that backup fails when duration > 60 seconds."""
        storage = Storage(70, 1)  # duration = 70 / 1 = 70 seconds
        duration, success = storage.start_backup()
        self.assertEqual(duration, 70)
        self.assertFalse(success)

    def test_boundary_conditions(self):
        """Test exact and near-boundary values."""
        # Exact boundary
        s1 = Storage(60, 1)
        duration1, success1 = s1.start_backup()
        self.assertEqual(duration1, 60)
        self.assertTrue(success1)
        
        # Just over/under boundary
        s2 = Storage(60.000001, 1)
        s3 = Storage(59.999999, 1)
        self.assertFalse(s2.start_backup()[1])
        self.assertTrue(s3.start_backup()[1])

    def test_duration_calculation(self):
        """Test the correctness of duration calculation."""
        storage = Storage(45, 1.5)  # duration = 45 / 1.5 = 30 seconds
        duration, _ = storage.start_backup()
        self.assertEqual(duration, 30)

    def test_negative_values(self):
        """Test negative info_size and storage_speed."""
        # Negative info_size
        s1 = Storage(-30, 1)
        duration1, success1 = s1.start_backup()
        self.assertEqual(duration1, -30)
        self.assertTrue(success1)  # Negative duration <= 60

        # Negative storage_speed
        s2 = Storage(30, -1)
        duration2, success2 = s2.start_backup()
        self.assertEqual(duration2, -30)
        self.assertTrue(success2)  # Negative duration <= 60

    def test_extreme_numbers(self):
        # Test very large and small numbers.
        huge = 1e308
        tiny = 1e-308
        
        s1 = Storage(huge, huge/30)  # Should take 30 seconds
        s2 = Storage(tiny, tiny/30)  # Should take 30 seconds
        self.assertTrue(s1.start_backup()[1])
        self.assertTrue(s2.start_backup()[1])

    def test_invalid_inputs(self):
        #Test invalid input handling.
        invalid = [None, "string", [], {}]
        for inv in invalid:
            with self.assertRaises((TypeError, ValueError)):
                Storage(inv, 1).start_backup()
                Storage(1, inv).start_backup()

    def test_zero_and_special_values(self):
        # Test zero, NaN, infinity, and other special cases.
        # Zero cases
        with self.assertRaises(ZeroDivisionError):
            Storage(10, 0).start_backup()
        
        self.assertTrue(Storage(0, 1).start_backup()[1])
        
        # NaN and Infinity cases
        s1 = Storage(float('nan'), 1)
        s2 = Storage(float('inf'), 1)
        s3 = Storage(100, float('inf'))
        
        dur1, suc1 = s1.start_backup()
        dur2, suc2 = s2.start_backup()
        dur3, suc3 = s3.start_backup()
        
        self.assertTrue(math.isnan(dur1))
        self.assertTrue(math.isinf(dur2))
        self.assertEqual(dur3, 0)
        
        self.assertFalse(suc1)  # NaN duration -> fail
        self.assertFalse(suc2)  # Infinite duration -> fail
        self.assertTrue(suc3)   # Zero duration -> success

if __name__ == "__main__":
    unittest.main(verbosity=2)
