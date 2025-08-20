import unittest
import tkinter as tk
from testableIC import MealDeliveryAdviceSystem
from unittest.mock import patch

class TestMealDeliveryAdviceSystem(unittest.TestCase):
    def setUp(self):
        # Set up the tkinter root window and initialize the application.
        # The main window is hidden using `withdraw` to prevent it from popping up during testing.
        self.main_window = tk.Tk()
        self.main_window.withdraw()  # Hide the main window during tests
        self.app = MealDeliveryAdviceSystem(self.main_window)

    def tearDown(self):
        # Destroy the tkinter window after each test to ensure there's no overlap between tests.
        self.main_window.destroy()

    def test_query_found(self):
        # Test that a known valid query triggers the expected response.
        # It checks if the application correctly identifies the question and displays the correct answer.
        self.app.query_input.insert(0, "What are the delivery fees?")
        with patch('tkinter.messagebox.showinfo') as mock_info:
            self.app.respond_to_question()
            mock_info.assert_called_once_with(
                "Solution",
                "Q: What are the delivery fees?\nA: Delivery fees are determined by the restaurant and area, typically ranging from $2 to $5."
            )

    def test_query_found_alternative(self):
        # Test another valid query to ensure the correct handling of different valid inputs.
        # This helps verify that the application can handle multiple valid questions accurately.
        self.app.query_input.insert(0, "What time is ideal to place orders to avoid wait times?")
        with patch('tkinter.messagebox.showinfo') as mock_info:
            self.app.respond_to_question()
            mock_info.assert_called_once_with(
                "Solution",
                "Q: What time is ideal to place orders to avoid wait times?\nA: Ordering outside peak times, like late afternoons, can lessen delay."
            )

    def test_query_not_found(self):
        # Test that an unrecognized query triggers a "Not Found" response.
        # This is important to verify the behavior of the system when the input doesn't match any known questions.
        self.app.query_input.insert(0, "Is there drone delivery?")
        with patch('tkinter.messagebox.showwarning') as mock_warning:
            self.app.respond_to_question()
            mock_warning.assert_called_once_with("Not Found", "Sorry, I can't find an answer to that query.")

    def test_empty_query(self):
        # Test if an empty input triggers a warning for the user to enter a question.
        # This is a validation test to ensure the application doesn't proceed with empty input.
        self.app.query_input.delete(0, tk.END)  # Ensure the input is empty
        with patch('tkinter.messagebox.showwarning') as mock_warning:
            self.app.respond_to_question()
            mock_warning.assert_called_once_with("Input Required", "Please enter a question before clicking 'Ask'.")

    def test_input_box_exists(self):
        # Check that the input box (Entry widget) is present and exists within the UI.
        # It's essential to verify that the widget is correctly initialized and ready to use.
        self.assertIsInstance(self.app.query_input, tk.Entry)
        self.assertTrue(self.app.query_input.winfo_exists())

    def test_ask_button_exists(self):
        # Check that the 'Ask' button is present in the UI.
        # Ensures that the button for triggering responses exists and is correctly initialized.
        self.assertIsInstance(self.app.ask_button, tk.Button)
        self.assertTrue(self.app.ask_button.winfo_exists())

if __name__ == "__main__":
    unittest.main(verbosity=2)
