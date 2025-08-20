import unittest
from unittest.mock import patch, MagicMock
import logging
import streamlit as st
from testableIc import reset_chat

# Function to suppress specific log messages
def suppress_streamlit_warnings():
    # Find all active loggers
    for name, logger in logging.Logger.manager.loggerDict.items():
        if isinstance(logger, logging.Logger):
            # Set loggers that include 'script_runner' in their name to ERROR level
            if "script_runner" in name or "streamlit" in name:
                logger.setLevel(logging.ERROR)


# Suppress warnings from Streamlit's ScriptRunContext
suppress_streamlit_warnings()


class TestStreamlitResetChat(unittest.TestCase):
    """Unit tests for checking reset_chat behavior with different session states."""

    @patch('streamlit.rerun')
    @patch('streamlit.session_state', new_callable=MagicMock)
    def test_reset_chat_with_multiple_messages(self, mock_session_state, mock_rerun):
        """Test if reset_chat triggers st.rerun and clears multiple session messages."""
        # Setting up multiple messages in session state before reset
        st.session_state.messages = [
            {"role": "user", "content": [{"type": "text", "text": "First message"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Assistant's reply to first message"}]},
            {"role": "user", "content": [{"type": "text", "text": "Second message"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Assistant's reply to second message"}]}
        ]
        st.session_state.suggestions = ["Suggestion 1", "Suggestion 2"]
        st.session_state.active_suggestion = "Test suggestion"

        reset_chat()

        # Verify that all messages and suggestions are cleared from session state
        self.assertEqual(st.session_state.messages, [], "Messages were not cleared after reset.")
        self.assertEqual(st.session_state.suggestions, [], "Suggestions were not cleared after reset.")
        self.assertIsNone(st.session_state.active_suggestion, "Active suggestion was not cleared after reset.")

        # Ensure that st.rerun was called
        self.assertTrue(mock_rerun.called,
            "st.rerun was not called after reset."
        )

    
    @patch('streamlit.rerun')
    @patch('streamlit.session_state', new_callable=MagicMock)
    def test_reset_chat_with_single_message(self, mock_session_state, mock_rerun):
        """Test if reset_chat correctly clears session state with a single message."""
        # Set up session state with a single message
        st.session_state.messages = [{"role": "user", "content": [{"type": "text", "text": "Single test message"}]}]
        st.session_state.suggestions = ["Single suggestion"]
        st.session_state.active_suggestion = "Test suggestion"

        reset_chat()

        # Check if session state values are reset
        self.assertEqual(st.session_state.messages, [], "Messages were not cleared after reset.")
        self.assertEqual(st.session_state.suggestions, [], "Suggestions were not cleared after reset.")
        self.assertIsNone(st.session_state.active_suggestion, "Active suggestion was not cleared after reset.")

        # Ensure that st.rerun was called
        self.assertTrue(mock_rerun.called,
            "st.rerun was called after reset."
        )

    
    @patch('streamlit.rerun')
    @patch('streamlit.session_state', new_callable=MagicMock)
    def test_reset_chat_with_no_messages(self, mock_session_state, mock_rerun):
        """Test if reset_chat works correctly when there are no messages or suggestions."""
        # Set up empty session state (no messages, suggestions, or active_suggestion)
        st.session_state.messages = []
        st.session_state.suggestions = []
        st.session_state.active_suggestion = None


        reset_chat()


        # Check if session state values remain reset
        self.assertEqual(st.session_state.messages, [], "Messages were not cleared after reset.")
        self.assertEqual(st.session_state.suggestions, [], "Suggestions were not cleared after reset.")
        self.assertIsNone(st.session_state.active_suggestion, "Active suggestion was not cleared after reset.")

        # Ensure that st.rerun was called
        self.assertTrue(mock_rerun.called,
            "st.rerun was called after reset."
        )

if __name__ == "__main__":
    unittest.main(verbosity=2)
