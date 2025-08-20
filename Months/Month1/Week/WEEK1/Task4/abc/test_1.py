import unittest
from unittest.mock import patch, MagicMock
import abc_de  # Import the module where your `aaa` function is located

class TestAaa(unittest.TestCase):
    @patch('abc_de.api')  # Patch the api function
    def test_aaa(self, mock_api):
        # Create a mock instance for the api return value
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
    unittest.main(verbosity=2)