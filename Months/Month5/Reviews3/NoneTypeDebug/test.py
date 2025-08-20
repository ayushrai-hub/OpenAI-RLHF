import unittest
import numpy as np
from io import StringIO
import sys
from TestableIC import process_material

class TestMaterialProcessing(unittest.TestCase):

    def setUp(self):
        self.captured_output = StringIO()
        sys.stdout = self.captured_output

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def test_process_cylinder(self):
        # Test the process_material function for a cylinder shape
        lengthData1_steel = np.array([3.18, 3.18, 3.19, 3.19, 3.18])
        dLength1_steel = np.array([0.01, 0.01, 0.01, 0.01, 0.01])
        diamData1_steel = np.array([1.28, 1.28, 1.27, 1.27, 1.28])
        dDiam1_steel = np.array([0.01, 0.01, 0.01, 0.01, 0.01])
        massData1_steel = np.array([11.01, 11.02, 10.98, 10.99, 10.95])
        dMass1_steel = np.array([0.01, 0.01, 0.01, 0.01, 0.01])

        process_material(lengthData1_steel, dLength1_steel, diamData1_steel, dDiam1_steel, massData1_steel, dMass1_steel)

        output = self.captured_output.getvalue()

        self.assertIn("Avg Mass: 10.99 g | Unc: 0.00 g", output)
        self.assertIn("Volume: 4.07 cm^3 | Unc: 0.02 cm^3", output)
        self.assertIn("Density: 2.70 g/cm^3 | Unc: 0.01 g/cm^3", output)

    def test_process_rectangle(self):
        # Test the process_material function for a rectangular shape
        lengthData1_nickel = np.array([3.18, 3.18, 3.19, 3.19, 3.18])
        dLength1_nickel = np.array([0.01, 0.01, 0.01, 0.01, 0.01])
        baseData1_nickel = np.array([1.28, 1.28, 1.27, 1.27, 1.28])
        dBase1_nickel = np.array([0.01, 0.01, 0.01, 0.01, 0.01])
        depthData1_nickel = np.array([1.28, 1.28, 1.27, 1.27, 1.28])
        dDepth1_nickel = np.array([0.01, 0.01, 0.01, 0.01, 0.01])
        massData1_nickel = np.array([39.03, 39.04, 39.03, 39.05, 39.03])
        dMass1_nickel = np.array([0.01, 0.01, 0.01, 0.01, 0.01])

        process_material(lengthData1_nickel, dLength1_nickel, None, None, massData1_nickel, dMass1_nickel,
                         form="rectangle", baseData=baseData1_nickel, dBase=dBase1_nickel,
                         depthData=depthData1_nickel, dDepth=dDepth1_nickel)

        output = self.captured_output.getvalue()

        self.assertIn("Avg Mass: 39.04 g | Unc: 0.00 g", output)
        self.assertIn("Volume: 5.18 cm^3 | Unc: 0.03 cm^3", output)
        self.assertIn("Density: 7.53 g/cm^3 | Unc: 0.04 g/cm^3", output)

    def test_process_sphere_with_hole(self):
        # Test the process_material function for a sphere with a hole shape
        diamSphereData1_unknown = np.array([3.18, 3.18, 3.19, 3.19, 3.18])
        dDiamSphereData1_unknown = np.array([0.01, 0.01, 0.01, 0.01, 0.01])
        diamHoleData1_unknown = np.array([1.28, 1.28, 1.27, 1.27, 1.28])
        dDiamHoleData1_unknown = np.array([0.01, 0.01, 0.01, 0.01, 0.01])
        massData1_unknown = np.array([59.01, 59.02, 59.03, 59.00, 59.00])
        dMass1_unknown = np.array([0.01, 0.01, 0.01, 0.01, 0.01])

        process_material(None, None, diamSphereData1_unknown, dDiamSphereData1_unknown, massData1_unknown,
                         dMass1_unknown, form="sphere_with_hole", diamHoleData=diamHoleData1_unknown,
                         dDiamHole=dDiamHoleData1_unknown)

        output = self.captured_output.getvalue()

        self.assertIn("Avg Mass: 59.01 g | Unc: 0.00 g", output)
        self.assertIn("Volume: 15.81 cm^3 | Unc: 0.06 cm^3", output)
        self.assertIn("Density: 3.73 g/cm^3 | Unc: 0.01 g/cm^3", output)

    def test_invalid_data_lengths(self):
        # Test if error is raised when data and uncertainty arrays have different lengths
        lengthData_invalid = np.array([3.18, 3.19, 3.18])
        dLength_invalid = np.array([0.01, 0.01])  # Incorrect length
        diamData_invalid = np.array([1.28, 1.28, 1.28])
        dDiam_invalid = np.array([0.01, 0.01, 0.01])
        massData_invalid = np.array([10.99, 11.00, 10.98])
        dMass_invalid = np.array([0.01, 0.01, 0.01])

        with self.assertRaises(ValueError) as context:
            process_material(lengthData_invalid, dLength_invalid, diamData_invalid, dDiam_invalid, massData_invalid, dMass_invalid)
        self.assertIn("Data and uncertainty arrays must have the same length", str(context.exception))

    def test_invalid_form_type(self):
        # Test if error is raised for invalid form type
        lengthData_valid = np.array([3.18, 3.18, 3.19, 3.19, 3.18])
        dLength_valid = np.array([0.01, 0.01, 0.01, 0.01, 0.01])
        diamData_valid = np.array([1.28, 1.28, 1.27, 1.27, 1.28])
        dDiam_valid = np.array([0.01, 0.01, 0.01, 0.01, 0.01])
        massData_valid = np.array([11.01, 11.02, 10.98, 10.99, 10.95])
        dMass_valid = np.array([0.01, 0.01, 0.01, 0.01, 0.01])

        with self.assertRaises(ValueError) as context:
            process_material(lengthData_valid, dLength_valid, diamData_valid, dDiam_valid, massData_valid, dMass_valid, form="invalid_shape")
        self.assertIn("Form must be one of: 'cylinder', 'rectangle', or 'sphere_with_hole'", str(context.exception))

if __name__ == "__main__":
    unittest.main(verbosity=2)