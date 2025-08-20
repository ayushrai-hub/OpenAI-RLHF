import unittest
from unittest.mock import Mock, patch
from tkinter import StringVar

# Import your QuizMaster class
from Quizgame import QuizMaster

class TestQuizMaster(unittest.TestCase):
    def setUp(self):
         # Create a mock Tk instance
        self.mock_tk = Mock()
        self.mock_tk.title = Mock()

        # Test vocabulary (ensure all words match the case in the tests)
        self.test_vocab = {
            "Python": "A high-level programming language",
            "Java": "A general-purpose programming language",
            "HTML": "The standard markup language for creating web pages",
            "CSS": "A style sheet language",
            "JavaScript": "A programming language for the web"
        }
        
         # Patch Tkinter-related classes and methods
         #replace `Quizgame` with the name of the file that will be tested
        self.patcher1 = patch('Quizgame.Label', Mock())
        self.patcher2 = patch('Quizgame.ttk.Entry', Mock())
        self.patcher3 = patch('Quizgame.ttk.Button', Mock())
        self.patcher4 = patch('Quizgame.StringVar', Mock())
        
        self.patcher1.start()
        self.patcher2.start()
        self.patcher3.start()
        self.patcher4.start()

        # Create QuizMaster instance
        self.quiz = QuizMaster(self.mock_tk, self.test_vocab)

        # Mock the entry_box
        self.quiz.entry_box = Mock()
        self.quiz.entry_box.get = Mock(return_value="")
    
    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()
        self.patcher4.stop()
    def test_leading_trailing_spaces(self):
        #  Verifies that leading and trailing spaces are properly handled
        # This is important to ensure user input with extra spaces is not marked as incorrect
        self.quiz.current_word = "Python"
        self.quiz.entry_box.get.return_value = "  Python  "
        self.quiz.validate_input()
        self.assertEqual(self.quiz.correct_answers, 1, "Failed to handle leading/trailing spaces")

        # Checks if multiple spaces between words are handled correctly
        # This ensures that the system can handle various types of spacing errors
        self.quiz.current_word = "Java"
        self.quiz.entry_box.get.return_value = "  Java  Script  "
        self.quiz.validate_input()
        self.assertEqual(self.quiz.correct_answers, 1, "Failed to handle multiple spaces between words")

        # Verifies that words with no extra spaces are still recognized correctly
        # This test ensures that the space-handling doesn't break correct inputs
        self.quiz.current_word = "CSS"
        self.quiz.entry_box.get.return_value = "CSS"
        self.quiz.validate_input()
        self.assertEqual(self.quiz.correct_answers, 2, "Failed to recognize word without extra spaces")


    def test_case_insensitivity(self):
        #  Checks if lowercase input is accepted for an uppercase word
        self.quiz.current_word = "HTML"
        self.quiz.entry_box.get.return_value = "html"
        self.quiz.validate_input()
        self.assertEqual(self.quiz.correct_answers, 1, "Failed to handle lowercase input")

        # Verifies that uppercase input is accepted for a lowercase word
        self.quiz.current_word = "Python"
        self.quiz.entry_box.get.return_value = "PYTHON"
        self.quiz.validate_input()
        self.assertEqual(self.quiz.correct_answers, 2, "Failed to handle uppercase input")

        # Checks if mixed case input is correctly recognized
        self.quiz.current_word = "JavaScript"
        self.quiz.entry_box.get.return_value = "jAvaScRiPt"
        self.quiz.validate_input()
        self.assertEqual(self.quiz.correct_answers, 3, "Failed to handle mixed case input")

    def test_mixed_case_and_spaces(self):
        # Verifies handling of mixed case with leading/trailing spaces
        self.quiz.current_word = "Python"
        self.quiz.entry_box.get.return_value = "  pYtHoN  "
        self.quiz.validate_input()
        self.assertEqual(self.quiz.correct_answers, 1, "Failed to handle mixed case with leading/trailing spaces")

        # Checks if the system can handle internal spaces with mixed case
        self.quiz.current_word = "JavaScript"
        self.quiz.entry_box.get.return_value = "Java  ScRiPt"
        self.quiz.validate_input()
        self.assertEqual(self.quiz.correct_answers, 2, "Failed to handle internal spaces with mixed case")

        # Verifies correct handling of acronyms with spaces and mixed case
        self.quiz.current_word = "CSS"
        self.quiz.entry_box.get.return_value = " c S s "
        self.quiz.validate_input()
        self.assertEqual(self.quiz.correct_answers, 3, "Failed to handle acronym with spaces and mixed case")

if __name__ == '__main__':
    unittest.main(verbosity=2)