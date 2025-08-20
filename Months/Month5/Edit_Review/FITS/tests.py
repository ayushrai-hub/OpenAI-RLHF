import unittest
from PyQt6.QtWidgets import QApplication
import sys
from ideal_completion import FitsManagerAndChangerApp 

app = QApplication(sys.argv)  

class TestFitsManagerAndChanger(unittest.TestCase):
    def setUp(self):
        # Create the GUI application to be tested.
        self.app = FitsManagerAndChangerApp()

    def test_default_radio_button_selection(self):
        # Test if the 'Lights' radio button is selected by default.
        self.assertTrue(self.app.radio_lights.isChecked())
        self.assertFalse(self.app.radio_flats.isChecked())

    def test_radio_button_labels(self):
        # Test the labels of the radio buttons to ensure they are correctly set.
        self.assertEqual(self.app.radio_flats.text(), "Flats")
        self.assertEqual(self.app.radio_lights.text(), "Lights")

    def test_filename_generation_for_lights(self):
        # Test the filename generation logic for 'Lights'.
        self.app.radio_lights.setChecked(True)
        self.app.object_id_input.setText("OBJ123")
        self.app.filter_name_input.setText("V")
        self.app.date_input.setText("01122023")
        filename = self.app.generate_filename(0, {'PIERSIDE': 'WEST'}, "OBJ123", "V", "01122023")
        expected_filename = "OBJ123_CAT_01122023_FILTER_V_EAST_0001.fits"
        self.assertEqual(filename, expected_filename)

    def test_filename_generation_for_flats(self):
        # Test the filename generation logic for 'Flats'.
        self.app.radio_flats.setChecked(True)
        self.app.object_id_input.setText("OBJ123")
        self.app.filter_name_input.setText("V")
        self.app.date_input.setText("01122023")
        filename = self.app.generate_filename(0, {}, "OBJ123", "V", "01122023")
        expected_filename = "FLAT_CAT_01122023_FILTER_V_0001.fits"
        self.assertEqual(filename, expected_filename)

    def test_radio_button_toggle(self):
        # Test that selecting one radio button deselects the other.
        self.app.radio_flats.setChecked(True)
        self.assertTrue(self.app.radio_flats.isChecked())
        self.assertFalse(self.app.radio_lights.isChecked())
        self.app.radio_lights.setChecked(True)
        self.assertTrue(self.app.radio_lights.isChecked())
        self.assertFalse(self.app.radio_flats.isChecked())

    def tearDown(self):
        """Clean up after tests."""
        self.app = None

if __name__ == '__main__':
    unittest.main(verbosity=2)