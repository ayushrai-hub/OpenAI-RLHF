import unittest
from unittest.mock import patch, MagicMock
from tkinter import Tk
from ideal  import QuizMaster  # Assume the main code is in quiz_master.py

class TestQuizMaster(unittest.TestCase):
    def setUp(self):
        self.root = Tk()
        self.vocab = {
            "Python": "A high-level programming language.",
            "Java": "A general-purpose programming language.",
            "HTML": "The standard markup language for creating web pages."
        }
        self.game = QuizMaster(self.root, self.vocab)

    def tearDown(self):
        self.root.destroy()

    def test_init(self):
        self.assertEqual(self.game.total_words, 3)
        self.assertEqual(self.game.correct_answers, 0)
        self.assertEqual(self.game.wrong_answers, 0)

    @patch('random.choice')
    def test_select_word_difficulty(self, mock_choice):
        mock_choice.return_value = ("Python", "A high-level programming language.")
        self.game.difficulty.set("Easy")
        self.game.select_word()
        mock_choice.assert_called_once()

        mock_choice.reset_mock()
        self.game.difficulty.set("Hard")
        self.game.select_word()
        mock_choice.assert_called_once()
 
    def test_validate_input_case_insensitive(self):
        self.game.current_word = "Python"
        self.game.input_var.set("PYTHON")
        self.game.validate_input()
        self.assertEqual(self.game.correct_answers, 1)
        self.assertEqual(self.game.wrong_answers, 0)

    def test_validate_input_extra_spaces(self):
        self.game.current_word = "Python"
        self.game.input_var.set("  Python  ")
        self.game.validate_input()
        self.assertEqual(self.game.correct_answers, 1)
        self.assertEqual(self.game.wrong_answers, 0)


    @patch('time.time')
    def test_add_score(self, mock_time):
        mock_time.return_value = 10  # Set a fixed time
        self.game.word_start_time = 5  # 5 seconds ago
        self.game.difficulty.set("Medium")
        with patch('builtins.print') as mock_print:
            self.game.add_score(1.0)  # Perfect match
            mock_print.assert_called_with("Word score: 30")

    def test_end_game(self):
        with patch('tkinter.messagebox.showinfo') as mock_showinfo:
            self.game.end_game()
            mock_showinfo.assert_called_once()

    def test_update_progress_bar(self):
        self.game.update_progress_bar()
        self.assertEqual(self.game.progress_bar["value"], 0)

        self.game.vocab.pop("Python")
        self.game.update_progress_bar()
        self.assertAlmostEqual(self.game.progress_bar["value"], 33.33, places=2)

if __name__ == '__main__':
    unittest.main(verbosity=2)