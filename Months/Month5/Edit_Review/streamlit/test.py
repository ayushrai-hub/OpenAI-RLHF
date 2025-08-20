import unittest
import os
from streamlit.testing.v1 import AppTest

class TestResetChat(unittest.TestCase):

    def setUp(self):
        # Initialize session state variables
        path = os.path.join(os.path.dirname(__file__), 'ideal_completion.py')
        self.app = AppTest.from_file(path, default_timeout=10)
        self.app.session_state.messages = [
            {"role": "user", "content": [{"text":"message1", "type": "text"}]},
            {"role": "assistant", "content": [{"text":"message2", "type": "text"}]}
        ]
        self.app.session_state.suggestions = ['suggestion1', 'suggestion2']
        self.app.session_state.active_suggestion = 'suggestion'
        self.app.run()

    def reset_chat(self):
        self.app.button[0].click().run()

    def test_reset_chat_clears_messages(self):
        """Test that reset button clears chat history"""
        self.reset_chat()
        self.assertEqual(self.app.session_state.messages, [])

    def test_reset_chat_clears_suggestions(self):
        """Test that reset button clears suggestion list"""
        self.reset_chat()
        self.assertEqual(self.app.session_state.suggestions, [])

    def test_reset_chat_clears_active_suggestion(self):
        """Test that reset button clears any active suggestion"""
        self.reset_chat()
        self.assertIsNone(self.app.session_state.active_suggestion)

    def test_reset_chat_runs_without_exception(self):
        """Test that reset button works without errors"""
        try:
            self.reset_chat()
        except Exception as e:
            self.fail(f"reset_chat() raised an exception: {e}")

    def test_chat_input_runs_without_exception(self):
        """Test that chat input still works after adding reset feature"""
        try:
            self.app.chat_input[0].set_value("test").run()
        except Exception as e:
            self.fail(f"chat_input.set_value() raised an exception: {e}")

    def test_single_reset_is_sufficient(self):
        """Test that a single reset clears all state completely"""
        # Set some initial state
        self.app.session_state.messages = [{"role": "user", "content": [{"text":"test", "type": "text"}]}]
        self.app.run()
        
        # First reset
        self.reset_chat()
        first_state = self.app.session_state.messages.copy()
        
        # Second reset
        self.reset_chat()
        second_state = self.app.session_state.messages.copy()
        
        # Both states should be empty lists
        self.assertEqual(first_state, [])
        self.assertEqual(second_state, [])
        self.assertEqual(first_state, second_state)

if __name__ == "__main__":
    unittest.main(verbosity=2)
