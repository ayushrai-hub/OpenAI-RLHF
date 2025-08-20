import unittest
from ideal_completion import orientation_gain_Mark, rotation_rate_gain_Mark

class TestMarkValues(unittest.TestCase):
    
    def test_orientation_gain_Mark(self):
        # Test for correct values in orientation_gain_Mark
        expected_values = {'x': 1.3441404603478013, 'y': 1.2614411737101796, 'z': 0.035}
        self.assertAlmostEqual(orientation_gain_Mark['x'], expected_values['x'])
        self.assertAlmostEqual(orientation_gain_Mark['y'], expected_values['y'])
        self.assertAlmostEqual(orientation_gain_Mark['z'], expected_values['z'])
    
    def test_rotation_rate_gain_Mark(self):
        # Test for correct values in rotation_rate_gain_Mark
        expected_values = {'x': 0.1930723592792962, 'y': 0.18226182860360546, 'z': 0.01}
        self.assertAlmostEqual(rotation_rate_gain_Mark['x'], expected_values['x'])
        self.assertAlmostEqual(rotation_rate_gain_Mark['y'], expected_values['y'])
        self.assertAlmostEqual(rotation_rate_gain_Mark['z'], expected_values['z'])

    def test_number_of_values(self):
        # Test that both dictionaries have exactly 3 values
        self.assertEqual(len(orientation_gain_Mark), 3)
        self.assertEqual(len(rotation_rate_gain_Mark), 3)

if __name__ == '__main__':
    unittest.main(verbosity=2)
