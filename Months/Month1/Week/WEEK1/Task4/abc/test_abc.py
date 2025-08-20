import unittest
from unittest.mock import patch, MagicMock
import abc_de  # Import the module where your `aaa` function is located

class TestAAAFunction(unittest.TestCase):
    @patch('abc_de.api')  # This is where you patch the `api` function
    def test_aaa(self, mock_api):
        # Create a mock instance of the `api` return value
        mock_nb = MagicMock()
        mock_api.return_value = mock_nb

        # Call the function you want to test
        abc_de.aaa()

        # Assert that `api` was called once
        mock_api.assert_called_once()

        # Assert that `graphql.query` was called on the instance returned by `api`
        mock_nb.graphql.query.assert_called_once()

        # Add more assertions as necessary to test the other code in `aaa`

if __name__ == '__main__':
    unittest.main()
