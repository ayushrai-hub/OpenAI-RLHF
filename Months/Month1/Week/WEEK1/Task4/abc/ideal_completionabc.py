import pytest
from unittest.mock import patch

import abc_de  # Import the module where your `aaa` function is located

@patch('abc_de.api')  # Patch the api function
def test_aaa(mock_api):
    # Create a mock instance for the api return value
    mock_nb = mock_api.return_value
    
    # Patch the graphql.query method on the mock api instance
    with patch.object(mock_nb.graphql, 'query') as mock_query:
        # Call the function you want to test
        abc_de.aaa()

        # Assert that `api` was called once
        mock_api.assert_called_once()

        # Assert that `graphql.query` was called on the instance returned by `api`
        mock_query.assert_called_once()

# This part is only necessary if you want to run pytest programmatically.
if __name__ == '__main__':
    pytest.main()
