import unittest
from unittest.mock import patch
from io import StringIO
import sys

# Assume the above code is in a file named number_guessing_game.py
from testable_ideal_random import NumberGuessingGame

class TestNumberGuessingGame(unittest.TestCase):

    @patch('builtins.input', side_effect=['50', '25', '75', '62', '68', '65'])
    @patch('random.randint', return_value=65)
    def test_successful_guess(self, mock_randint, mock_input):
        game = NumberGuessingGame()
        captured_output = StringIO()
        sys.stdout = captured_output
        game.play()
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("Congratulations! You guessed the correct number in 6 attempts.", output)

    @patch('builtins.input', side_effect=['abc', '50', 'quit'])
    @patch('random.randint', return_value=65)
    def test_invalid_input(self, mock_randint, mock_input):
        game = NumberGuessingGame()
        captured_output = StringIO()
        sys.stdout = captured_output
        game.play()
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("Invalid input. Please enter a valid number.", output)

    @patch('builtins.input', side_effect=['0', '101', '50', 'quit'])
    @patch('random.randint', return_value=65)
    def test_out_of_range_input(self, mock_randint, mock_input):
        game = NumberGuessingGame()
        captured_output = StringIO()
        sys.stdout = captured_output
        game.play()
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("Please enter a number between 1 and 100.", output)

    @patch('builtins.input', side_effect=['quit'])
    @patch('random.randint', return_value=65)
    def test_quit_game(self, mock_randint, mock_input):
        game = NumberGuessingGame()
        captured_output = StringIO()
        sys.stdout = captured_output
        game.play()
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("Game Over. Thank you for playing!", output)

if __name__ == '__main__':
    unittest.main(verbosity=2)