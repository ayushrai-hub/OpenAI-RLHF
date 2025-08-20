import unittest
from ideal_completion import compute_complex_number  
import math 

class TestComputeComplexNumber(unittest.TestCase):
    def test_zero_angle(self):
        """Test with angle zero degrees which should result in a real number only."""
        result = compute_complex_number(1e9, 0)
        expected_real_part = int(math.cos(0) * 32767)
        expected_imag_part = int(math.sin(0) * 32767)
        expected = (expected_real_part << 16) | (expected_imag_part & 0xFFFF)
        self.assertEqual(result, expected)

    def test_full_circle(self):
        """Test with 360 degrees to ensure it wraps correctly to zero."""
        result = compute_complex_number(1e9, 360)
        expected = compute_complex_number(1e9, 0)
        self.assertEqual(result, expected)

    def test_invalid_frequency(self):
        """Test with zero or negative frequency which should raise ValueError."""
        with self.assertRaises(ValueError):
            compute_complex_number(0, 0)
        with self.assertRaises(ValueError):
            compute_complex_number(-1e9, 90)

if __name__ == '__main__':
    unittest.main(verbosity=2)