import unittest
from testableIC import calculate_cross_section_dimensions

class TestCrossSectionDimensions(unittest.TestCase):
    def test_square_dimensions(self):
        # Test with no fixed dimensions to check for square cross-section calculation.
        flow_rate = 1.0 
        fluid_velocity = 2.0  
        expected_area = 0.5  
        expected_dimension = expected_area**0.5
        width, height = calculate_cross_section_dimensions(flow_rate, fluid_velocity)
        self.assertAlmostEqual(width, expected_dimension)
        self.assertAlmostEqual(height, expected_dimension)

    def test_fixed_width(self):
        # Test with fixed width to verify height calculation.
        flow_rate = 1.0  
        fluid_velocity = 2.0  
        fixed_width = 0.5  
        expected_area = 0.5
        expected_height = expected_area / fixed_width
        width, height = calculate_cross_section_dimensions(flow_rate, fluid_velocity, fixed_dimension=fixed_width, is_width=True)
        self.assertEqual(width, fixed_width)
        self.assertAlmostEqual(height, expected_height)

    def test_fixed_height(self):
        # Test with fixed height to verify width calculation.
        flow_rate = 1.0 
        fluid_velocity = 2.0 
        fixed_height = 0.5  
        expected_area = 0.5  
        expected_width = expected_area / fixed_height
        width, height = calculate_cross_section_dimensions(flow_rate, fluid_velocity, fixed_dimension=fixed_height, is_width=False)
        self.assertEqual(height, fixed_height)
        self.assertAlmostEqual(width, expected_width)

if __name__ == "__main__":
    unittest.main(verbosity=2)