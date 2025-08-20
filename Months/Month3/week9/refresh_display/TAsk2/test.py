import unittest
from unittest.mock import patch, MagicMock
from tkinter import Tk, StringVar
from code55 import QuizMaster  # Replace 'your_module' with the actual module name

class TestQuizMaster(unittest.TestCase):
    def setUp(self):
        self.root = MagicMock(spec=Tk)
        self.string_var = MagicMock(spec=StringVar)
        
        self.label_patcher = patch('tkinter.Label')
        self.entry_patcher = patch('tkinter.ttk.Entry')
        self.button_patcher = patch('tkinter.ttk.Button')
        
        self.mock_label = self.label_patcher.start()
        self.mock_entry = self.entry_patcher.start()
        self.mock_button = self.button_patcher.start()
        
        self.test_vocab = {
            "Python": "A programming language",
            "JAVA": "Another programming language",
            "HTML": "Markup language"
        }
        
        self.quiz_master = QuizMaster(self.root, self.test_vocab)
        self.quiz_master.input_var = self.string_var

    def tearDown(self):
        self.label_patcher.stop()
        self.entry_patcher.stop()
        self.button_patcher.stop()

    def test_leading_trailing_spaces(self):
        self.quiz_master.current_word = "Python"
        self.string_var.get.return_value = "  Python  "
        self.quiz_master.validate_input()
        self.assertEqual(self.quiz_master.correct_answers, 1)

        self.quiz_master.current_word = "JAVA"
        self.string_var.get.return_value = "  JAVA  "
        self.quiz_master.validate_input()
        self.assertEqual(self.quiz_master.correct_answers, 2)

        self.quiz_master.current_word = "HTML"
        self.string_var.get.return_value = "HTML"
        self.quiz_master.validate_input()
        self.assertEqual(self.quiz_master.correct_answers, 3)

    def test_case_insensitivity(self):
        self.quiz_master.current_word = "Python"
        self.string_var.get.return_value = "python"
        self.quiz_master.validate_input()
        self.assertEqual(self.quiz_master.correct_answers, 1)

        self.quiz_master.current_word = "JAVA"
        self.string_var.get.return_value = "java"
        self.quiz_master.validate_input()
        self.assertEqual(self.quiz_master.correct_answers, 2)

        self.quiz_master.current_word = "HTML"
        self.string_var.get.return_value = "HtMl"
        self.quiz_master.validate_input()
        self.assertEqual(self.quiz_master.correct_answers, 3)

    def test_mixed_case_and_spaces(self):
        self.quiz_master.current_word = "Python"
        self.string_var.get.return_value = "  pYtHoN  "
        self.quiz_master.validate_input()
        self.assertEqual(self.quiz_master.correct_answers, 1)

        self.quiz_master.current_word = "JAVA"
        self.string_var.get.return_value = "  J a V a  "
        self.quiz_master.validate_input()
        self.assertEqual(self.quiz_master.correct_answers, 2)

        self.quiz_master.current_word = "HTML"
        self.string_var.get.return_value = "  H t M l  "
        self.quiz_master.validate_input()
        self.assertEqual(self.quiz_master.correct_answers, 3)

if __name__ == '__main__':
    unittest.main(verbosity=2)