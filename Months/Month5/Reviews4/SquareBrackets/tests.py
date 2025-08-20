import unittest
from unittest.mock import patch, call

from testableIC import extract_value, get_base_name, processing

class TestIdealCompletion(unittest.TestCase):

    def test_get_base_name(self):
        # Test the get_base_name function to ensure it correctly removes brackets
        filename = 'file[A].pdf'
        base_name = get_base_name(filename)
        self.assertEqual(base_name, 'file.pdf')

    @patch('shutil.move')
    @patch('os.makedirs')
    @patch('os.listdir')
    def test_processing(self, mock_listdir, mock_makedirs, mock_move):
        # Mocking os.listdir to return a predefined set of files
        mock_listdir.return_value = [
            'file[A].pdf',
            'file[5].pdf',
            'other[B].pdf',
            'other[7].pdf'
        ]

        # Mock the directory creation function
        mock_makedirs.return_value = None

        # Call the processing function with the mocked directory
        processing('./')

        # Ensure the correct files were moved based on the conditions
        mock_move.assert_has_calls([
            call('./file[A].pdf', './_SS'),
            call('./other[B].pdf', './_SS')
        ], any_order=True)

        # Ensure that the _SS directory was created
        mock_makedirs.assert_called_once_with('./_SS', exist_ok=True)

if __name__ == '__main__':
    unittest.main()
