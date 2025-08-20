import unittest
from unittest.mock import patch
from ideal_completion import guest_directory, process_guest 

class TestGuestCatalog(unittest.TestCase):

    def setUp(self):
        """Reset the guest directory before each test."""
        guest_directory.clear()
        guest_directory.update({
            'Max': 2334,
            'Sam': 7234,
            'Leo': 9026,
            'Eva': 8213
        })

    @patch('builtins.input', side_effect=['Max', '2334','Max', '2334'])
    def test_name_already_present(self, mock_input):
        """Test when the guest name is already in the catalog."""
        with patch('builtins.print') as mock_print:
            process_guest()
            mock_print.assert_any_call('Your invitation code is 2334, Welcome Max to the event!!')


    @patch('builtins.input', side_effect=['John', '2334','John', '2334'])
    def test_new_name_existing_id(self, mock_input):
        """Test adding a new guest with an already existing ID."""
        with patch('builtins.print') as mock_print:
            process_guest()
            mock_print.assert_any_call("This ID is being used already. Please try another one.")
            self.assertNotIn('John', guest_directory)

    @patch('builtins.input', side_effect=['Max', '1234','Max', '1234'])
    def test_existing_name_new_id(self, mock_input):
        """Test when a new ID is entered but the name already exists."""
        with patch('builtins.print') as mock_print:
            process_guest()
            mock_print.assert_any_call("The name already included in guests list. Please provide correct ID with the name.")

    @patch('builtins.input', side_effect=['John', '9999','John', '9999'])
    def test_new_guest_new_id(self, mock_input):
        """Test adding a new guest with a new ID."""
        with patch('builtins.print') as mock_print:
            process_guest()
            mock_print.assert_any_call("The new guest John has been added with ID 9999.")
            self.assertIn('John', guest_directory)
            self.assertEqual(guest_directory['John'], 9999)

if __name__ == '__main__':
    unittest.main(verbosity=2)