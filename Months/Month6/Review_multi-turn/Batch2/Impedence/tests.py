import unittest
import numpy as np
from ideal_completion import compute_neutral_impedance

class TestNeutralImpedanceFunctions(unittest.TestCase):

    # Invalid Input Test Cases
    def test_empty_input_arrays(self):
        """Test with empty input arrays, expecting NaN result."""
        # Test to verify handling of empty input arrays. Since impedance can't
        # be computed without data, a NaN result is expected to indicate invalid input.
        v = np.array([])
        i_a = np.array([])
        i_b = np.array([])
        result = compute_neutral_impedance(v, i_a, i_b)
        self.assertTrue(np.isnan(result), "Expected NaN when input arrays are empty.")

    def test_inconsistent_array_lengths(self):
        """Test with arrays of different lengths, expecting NaN result."""
        # Test to confirm the function checks for consistent array lengths.
        # Impedance computation requires corresponding voltage and current data points,
        # so inconsistent array lengths should return NaN as an error response.
        v = np.full(10, 240.0)
        i_a = np.full(9, 10.0)   # One less element than v
        i_b = np.full(10, 8.0)
        result = compute_neutral_impedance(v, i_a, i_b)
        self.assertTrue(np.isnan(result), "Expected NaN for inconsistent array lengths.")

    def test_negative_voltage_or_current(self):
        """Test with negative values in v, i_a, or i_b, expecting NaN result."""
        # Tests handling of negative values in voltage/current, which are typically
        # physically unrealistic for RMS calculations. The function should return NaN
        # to indicate invalid physical parameters.
        v = np.full(10, -240.0)  # Negative voltage
        i_a = np.full(10, 10.0)
        i_b = np.full(10, 8.0)
        result = compute_neutral_impedance(v, i_a, i_b)
        self.assertTrue(np.isnan(result), "Expected NaN when RMS voltage is negative.")

    def test_zero_current_input(self):
        """Test with zero current in i_a and i_b, expecting NaN result."""
        # Test to verify function's response to zero current. With zero current,
        # impedance calculation would lead to a division by zero. NaN result is expected
        # to indicate invalid input due to zero current values.
        v = np.full(10, 240.0)  # RMS voltage between lines (V)
        i_a = np.full(10, 0.0)  # Zero current on phase A (A)
        i_b = np.full(10, 0.0)  # Zero current on phase B (A)
        result = compute_neutral_impedance(v, i_a, i_b)
        self.assertTrue(np.isnan(result), "Expected NaN for zero current input")

    def test_large_array(self):
        """Test with a large array to verify performance and consistency."""
        # Performance and stability test with large data arrays.
        # This ensures that the function efficiently handles large inputs
        # without running into memory issues or producing invalid results.
        v = np.full(10000, 240.0)
        i_a = np.random.normal(10, 0.5, 10000)
        i_b = np.random.normal(8, 0.5, 10000)
        result = compute_neutral_impedance(v, i_a, i_b)
        self.assertTrue(np.isfinite(result), "Result should be finite for large valid arrays")

    def test_unbalanced_load(self):
        """Test with unbalanced load, expecting a non-zero neutral impedance."""
        # Test for unbalanced load scenario, where current in phases differs.
        # The impedance should be non-zero for an unbalanced load, indicating
        # the function can correctly compute for real-world scenarios of load imbalance.
        v = np.full(10, 240.0)  # RMS voltage between lines (V)
        i_a = np.full(10, 15.0)  # Higher current on phase A (A)
        i_b = np.full(10, 5.0)   # Lower current on phase B (A)
        result = compute_neutral_impedance(v, i_a, i_b)
        self.assertGreater(result, 0, "Expected non-zero impedance for unbalanced load")

    
# Run the tests
if __name__ == "__main__":
    unittest.main(verbosity=2)