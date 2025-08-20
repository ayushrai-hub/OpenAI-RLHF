import unittest
from unittest.mock import MagicMock, patch
from tkinter import Tk
from ideal_code import QuizMaster  # Assuming the improved code is in a file named improved_quiz_master.py

class TestQuizMaster(unittest.TestCase):

    def setUp(self):
        self.root = Tk()
        self.vocab = {
            "Python": "A high-level programming language.",
            "Java": "A general-purpose programming language.",
            "HTML": "The standard markup language for creating web pages."
        }
        self.quiz = QuizMaster(self.root, self.vocab)

    def tearDown(self):
        self.root.destroy()

    def test_init(self):
        self.assertEqual(self.quiz.total_words, 3)
        self.assertEqual(self.quiz.correct_answers, 0)
        self.assertEqual(self.quiz.incorrect_answers, 0)

    def test_compare_words(self):
        self.assertTrue(QuizMaster.compare_words("python", "Python"))
        self.assertTrue(QuizMaster.compare_words(" Java ", "java"))
        self.assertTrue(QuizMaster.compare_words("HTML", "html"))
        self.assertFalse(QuizMaster.compare_words("Python", "Java"))    

    @patch('random.choice')
    def test_select_word(self, mock_choice):
        mock_choice.return_value = ("Python", "A high-level programming language.")
        word, hint = self.quiz.select_word()
        self.assertEqual(word, "Python")
        self.assertEqual(hint, "A high-level programming language.")

    def test_refresh_display_with_words(self):
        self.quiz.refresh_display()
        self.assertIn(self.quiz.current_word, self.quiz.vocab)
        self.assertNotEqual(self.quiz.hint_label.cget("text"), "")

    def test_refresh_display_no_words(self):
        self.quiz.vocab.clear()
        self.quiz.refresh_display()
        self.assertEqual(self.quiz.hint_label.cget("text"), "Bravo! You've guessed all the words.")

if __name__ == '__main__':
    unittest.main(verbosity=2)