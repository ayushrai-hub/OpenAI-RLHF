import os
import unittest
from ideal_completion import get_chatgpt_response

class TestChatGPTResponse(unittest.TestCase):

    def test_valid_response(self):
        prompt = "What is the capital of France?"
        get_chatgpt_response(prompt)

    def test_correct_response(self):
        prompt = "What is the capital of France?"
        response = get_chatgpt_response(prompt)
        self.assertIn("Paris", response)

if __name__ == '__main__':
    unittest.main()