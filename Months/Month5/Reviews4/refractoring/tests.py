import unittest
from testableIc import PlateMap

class TestPlateMap(unittest.TestCase):

    def test_compile_conditions_case1(self):
        # Input data
        sample_plate_map_data = {
            "A1": {"condition_1": "Control", "condition_2": "Treatment_A"},
            "A2": {"condition_1": "Control", "condition_2": "Treatment_B"},
            "A3": {"condition_1": "Control", "condition_2": "Treatment_A"},
            "B1": {"condition_1": "Test", "condition_2": "Treatment_C"},
            "B2": {"condition_1": "Test", "condition_2": "Treatment_B"},
        }

        # Expected output
        expected_output = ['Treatment_A', 'Treatment_B', 'Treatment_C']

        # Initialize the class with the sample data
        plate_map = PlateMap(sample_plate_map_data)

        # Run the method and check the output
        self.assertEqual(plate_map._compile_conditions(), expected_output)

    def test_compile_conditions_case2(self):
        # Input data
        sample_plate_map_data = {
            "C1": {"condition_1": "Placebo", "condition_2": "Treatment_X"},
            "C2": {"condition_1": "Placebo", "condition_2": "Treatment_Y"},
            "C3": {"condition_1": "Drug", "condition_2": "Treatment_Z"},
            "D1": {"condition_1": "Drug", "condition_2": "Treatment_Y"},
            "D2": {"condition_1": "Placebo", "condition_2": "Treatment_X"},
            "D3": {"condition_1": "Placebo", "condition_2": "Treatment_W"},
        }

        # Expected output
        expected_output = ['Treatment_X', 'Treatment_Y', 'Treatment_Z', 'Treatment_W']

        # Initialize the class with the sample data
        plate_map = PlateMap(sample_plate_map_data)

        # Run the method and check the output
        self.assertEqual(plate_map._compile_conditions(), expected_output)

if __name__ == '__main__':
    unittest.main(verbosity=2)