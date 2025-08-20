import unittest
import json
import os

# Load JSON data dynamically using the os module
def load_json_data():
    json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ideal_completion.json")  # Build the file path

    if not os.path.exists(json_file_path):
        raise FileNotFoundError(f"The file {json_file_path} does not exist.")

    with open(json_file_path, "r", encoding="utf-8") as file:
        return json.load(file)

json_data = load_json_data()

class TestJSONValidation(unittest.TestCase):

    def test_valid_json_list(self):
        """Test to validate if each item in the list is a valid JSON object."""
        for idx, json_obj in enumerate(json_data):
            try:
                json_string = json.dumps(json_obj)  # Convert each dictionary back to JSON string
                json.loads(json_string)  # Validate if it can be loaded back
            except ValueError:
                self.fail(f"Item at index {idx} is not a valid JSON")

    def test_json_data_not_empty(self):
        """Test to check if json_data list is not empty."""
        self.assertGreater(len(json_data), 0, "json_data should not be empty")

    def test_assistant_correct_content(self):
        """Test to verify that the assistant correctly got all the text content from the original user prompt."""
        expected_data1 = [
            {
                "role": "system",
                "content": "You are a handy assistant for generating test cases.\nYou solely respond with tests written in python code.\nAlways insert all tests within consistent readme markers.\n\njust like this:\n```python\nassert is_multiple_of([1.0, 2.0, 3.0], 0.5) == True\nassert is_multiple_of([1.2, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3) == False\n```\nUpon request to widen the test cases, provide additional ones, alongside the previous ones.\nWhen requested to narrow down the test cases, you offer only the most pertinent options.\nAvoid providing excessive test cases.\nExclude any information outside the specified tags."
            },
            {
                "role": "user",
                "content": "Develop test cases for the following function\n\nfrom typing import List\n\n\ndef below_zero(operations: List[int]) -> bool:\n    ``` You're given a list detailing deposit and withdrawal activities on a bank account which initially\n    has zero balance. Your mission is to determine if at anytime the account balance dips below zero, prompting\n    the function to return True. Otherwise, it should return False.\n    >>> below_zero([1, 2, 3])\n    False\n    >>> below_zero([1, 2, -4, 5])\n    True\n    ```\n"
            },
            {
                "role": "user",
                "content": "Expand the test cases"
            },
            {
                "role": "user",
                "content": "Reduce the test cases"
            }
        ]
        expected_data2 = [
            {
                "role": "system",
                "content": "You are a handy assistant for generating test cases.\nYou solely respond with tests written in python code.\nAlways insert all tests within consistent readme markers.\n\njust like this:\n```python\nassert is_multiple_of([1.0, 2.0, 3.0], 0.5) == True\nassert is_multiple_of([1.2, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3) == False\n```\nUpon request to widen the test cases, provide additional ones, alongside the previous ones.\nWhen requested to narrow down the test cases, you offer only the most pertinent options.\nAvoid providing excessive test cases.\nExclude any information outside the specified tags."
            },
            {
                "role": "user",
                "content": "Develop test cases for the following function\n\nfrom typing import List\n\n\ndef below_zero(operations: List[int]) -> bool:\n    \"\"\" You're given a list detailing deposit and withdrawal activities on a bank account which initially\n    has zero balance. Your mission is to determine if at anytime the account balance dips below zero, prompting\n    the function to return True. Otherwise, it should return False.\n    >>> below_zero([1, 2, 3])\n    False\n    >>> below_zero([1, 2, -4, 5])\n    True\n    \"\"\"\n"
            },
            {
                "role": "user",
                "content": "Expand the test cases"
            },
            {
                "role": "user",
                "content": "Reduce the test cases"
            }
        ]

        self.assertTrue(json_data == expected_data1 or json_data == expected_data2, "json_data does not match either expected_data1 or expected_data2")

if __name__ == "__main__":
    unittest.main(verbosity=2)