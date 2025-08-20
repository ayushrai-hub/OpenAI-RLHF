import unittest
from unittest.mock import patch, MagicMock, mock_open
import ideal_completion
import json
import time
import requests

class TestIdealCompletion(unittest.TestCase):

    @patch('ideal_completion.webdriver.Chrome')
    def test_fetch_bearer_token_success(self, mock_chrome):
        # Mock the WebDriver and its methods
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        # Simulate localStorage keys and values
        mock_driver.execute_script.side_effect = [
            ['token_12345'],  # Keys in localStorage
            json.dumps({'value': 'test_token_value'})  # Stored token value
        ]

        token = ideal_completion.fetch_bearer_token('http://example.com')
        self.assertEqual(token, 'test_token_value')
        mock_driver.get.assert_called_with('http://example.com')
        mock_driver.quit.assert_called_once()

    @patch('ideal_completion.webdriver.Chrome')
    def test_fetch_bearer_token_no_token(self, mock_chrome):
        # Mock the WebDriver and its methods
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        # Simulate no keys in localStorage
        mock_driver.execute_script.return_value = []

        token = ideal_completion.fetch_bearer_token('http://example.com')
        self.assertEqual(token, 'Token key not found')
        mock_driver.get.assert_called_with('http://example.com')
        mock_driver.quit.assert_called_once()

    @patch('ideal_completion.requests.post')
    def test_send_request_success(self, mock_post):
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.json.return_value = {'status': 'success'}
        mock_response.raise_for_status = lambda: None  # No exception raised

        mock_post.return_value = mock_response

        headers = {'Authorization': 'Bearer test_token'}
        url = 'https://example.site/api/bonuses/tokens/'
        payload = {'tokens': 915}

        response = ideal_completion.send_request(headers, url, payload)
        self.assertEqual(response, {'status': 'success'})
        mock_post.assert_called_with(url, json=payload, headers=headers)

    @patch('ideal_completion.requests.post')
    def test_send_request_failure(self, mock_post):
        # Simulate an exception during the POST request
        mock_post.side_effect = requests.exceptions.RequestException('Test Error')

        headers = {'Authorization': 'Bearer test_token'}
        url = 'https://example.site/api/bonuses/tokens/'
        payload = {'tokens': 915}

        response = ideal_completion.send_request(headers, url, payload)
        self.assertEqual(response, {})
        mock_post.assert_called_with(url, json=payload, headers=headers)

    @patch('ideal_completion.fetch_bearer_token')
    @patch('ideal_completion.send_request')
    def test_handle_accounts(self, mock_send_request, mock_fetch_bearer_token):
        # Mock the token fetch to return a test token
        mock_fetch_bearer_token.return_value = 'test_token_value'

        # Mock send_request to return a predefined response
        mock_send_request.return_value = {'detail': {'need_invites': 5, 'blocked_until': time.time() + 60}}

        # Mock account data
        account_data = (
    "user%3D%7B%22first_name%22%3A%22John%22%2C%22id%22%3A45678%7D\n"
    "user%3D%7B%22first_name%22%3A%22Jane%22%2C%22id%22%3A12345%7D"
)


        # Use mock_open to simulate reading from a file
        with patch('builtins.open', mock_open(read_data=account_data)):
            # Mock time.sleep to speed up the test
            with patch('time.sleep', return_value=None):
                ideal_completion.handle_accounts('account_data.txt')

        mock_fetch_bearer_token.assert_called()
        mock_send_request.assert_called()

if __name__ == "__main__":
    unittest.main(verbosity=2)
