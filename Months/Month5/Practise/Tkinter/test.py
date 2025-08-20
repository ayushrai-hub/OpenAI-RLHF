import unittest
from datetime import datetime, timedelta
import tkinter as tk
from unittest.mock import MagicMock, patch
import json
import os
import tempfile
from ideal_completion import SecurityManager, MessageBoardInterface

class TestSecurityManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.credentials_path = os.path.join(self.temp_dir, 'credentials.json')
        with patch('os.path.exists', return_value=False):
            self.security_manager = SecurityManager()

    def tearDown(self):
        if os.path.exists(self.credentials_path):
            os.remove(self.credentials_path)
        os.rmdir(self.temp_dir)

    def test_hash_password(self):
        # It tests the password hashing functionality
        password = "testpass"
        hashed = self.security_manager.hash_password(password)
        self.assertNotEqual(password, hashed)
        self.assertEqual(hashed, self.security_manager.hash_password(password))

    def test_verify_user_staff(self):
        # It tests the staff user verification
        with patch.dict(self.security_manager.user_credentials, {
            'staff': {'admin': self.security_manager.hash_password('staffsecret')},
            'pupil': {}
        }):
            self.assertTrue(
                self.security_manager.verify_user('admin', 'staffsecret', True)
            )
            self.assertFalse(
                self.security_manager.verify_user('admin', 'wrongpass', True)
            )

    def test_verify_user_pupil(self):
        # It tests the pupil user verification.
        with patch.dict(self.security_manager.user_credentials, {
            'staff': {},
            'pupil': {'12345': self.security_manager.hash_password('pupilpass')}
        }):
            self.assertTrue(
                self.security_manager.verify_user('12345', 'pupilpass', False)
            )
            # Test non-numeric pupil ID
            with patch('tkinter.messagebox.showerror'):  # Mock error dialog
                self.assertFalse(
                    self.security_manager.verify_user('abc', 'pupilpass', False)
                )

    @patch('builtins.open')
    def test_load_credentials(self, mock_open):
        # Test credential loading functionality"""
        test_credentials = {
            'staff': {'test': 'hash1'},
            'pupil': {'54321': 'hash2'}
        }
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(test_credentials)
        
        with patch('os.path.exists', return_value=True):
            self.security_manager.user_credentials = {}
            self.security_manager.load_or_create_credentials()
            self.assertEqual(self.security_manager.user_credentials, test_credentials)

class TestMessageBoardInterface(unittest.TestCase):
    @patch('tkinter.Listbox')
    def setUp(self, mock_listbox):
        self.root = tk.Tk()
        self.interface = MessageBoardInterface(self.root, 'test_user', True)
        # Prevent initial announcements from loading
        self.interface.announcements = []
        # Mock the listbox to prevent GUI interactions
        self.interface.announcement_listbox = mock_listbox

    def tearDown(self):
        self.root.destroy()

    def test_add_announcement(self):
        # It tests adding announcements
        # It Mock entry widgets
        self.interface.announcement_entry = MagicMock()
        self.interface.datefield_entry = MagicMock()
        self.interface.timefield_entry = MagicMock()
        
        # It sets the test values
        future_time = datetime.now() + timedelta(hours=1)
        self.interface.announcement_entry.get.return_value = "Test Announcement"
        self.interface.datefield_entry.get.return_value = future_time.strftime('%d/%m/%Y')
        self.interface.timefield_entry.get.return_value = future_time.strftime('%I:%M %p')
        
        # It clears existing announcements
        self.interface.announcements = []
        
        # Add announcement
        self.interface.add_announcement()
        
        # It verifies single announcement was added
        self.assertEqual(len(self.interface.announcements), 1)
        self.assertEqual(self.interface.announcements[0]['text'], "Test Announcement")

    def test_delete_announcement(self):
        # It tests the deleting announcements.
        # It clears existing announcements
        self.interface.announcements = []
        
        # It adds test announcement
        test_announcement = {
            'text': 'Test Announcement',
            'expiry': datetime.now() + timedelta(hours=1),
            'user': 'test_user'
        }
        self.interface.announcements.append(test_announcement)
        
        # Mock listbox selection
        self.interface.announcement_listbox.curselection.return_value = (0,)
        
        # Delete announcement
        self.interface.delete_announcement()
        
        # It verifies announcement was deleted
        self.assertEqual(len(self.interface.announcements), 0)

    def test_expired_announcements(self):
        # It tests  expired announcement handling.
        # It clears existing announcements
        self.interface.announcements = []
        
        # It adds the expired and valid announcements
        expired_announcement = {
            'text': 'Expired Announcement',
            'expiry': datetime.now() - timedelta(minutes=1),
            'user': 'test_user'
        }
        valid_announcement = {
            'text': 'Valid Announcement',
            'expiry': datetime.now() + timedelta(hours=1),
            'user': 'test_user'
        }
        
        self.interface.announcements.extend([expired_announcement, valid_announcement])
        
        # It checks the expired announcements
        self.interface.verify_expired_announcements()
        
        # It verifies the only valid announcement remains
        self.assertEqual(len(self.interface.announcements), 1)
        self.assertEqual(self.interface.announcements[0]['text'], 'Valid Announcement')

    @patch('tkinter.simpledialog.askstring')
    def test_modify_announcement(self, mock_askstring):
        # It tests the modifying announcements.
        # this clears the existing announcements
        self.interface.announcements = []
        
        # It adds the test announcement
        test_announcement = {
            'text': 'Original Announcement',
            'expiry': datetime.now() + timedelta(hours=1),
            'user': 'test_user'
        }
        self.interface.announcements.append(test_announcement)
        
        # Mock listbox selection and dialog
        self.interface.announcement_listbox.curselection.return_value = (0,)
        mock_askstring.return_value = 'Modified Announcement'
        
        # It modifies announcement
        self.interface.modify_announcement()
        
        # It verifies the announcement was modified
        self.assertEqual(self.interface.announcements[0]['text'], 'Modified Announcement')

    def test_swap_view(self):
        # It tests view switching functionality"""
        # Mock required widgets
        self.interface.announcement_entry = MagicMock()
        self.interface.datefield_entry = MagicMock()
        self.interface.timefield_entry = MagicMock()
        self.interface.insert_button = MagicMock()
        self.interface.delete_button = MagicMock()
        self.interface.modify_button = MagicMock()
        self.interface.swap_view_button = MagicMock()
        
        # Initial state (staff view)
        self.assertTrue(self.interface.is_staff)
        
        # Switch to pupil view
        self.interface.swap_view()
        self.assertFalse(self.interface.is_staff)
        
        # Switch back to staff view
        self.interface.swap_view()
        self.assertTrue(self.interface.is_staff)

if __name__ == '__main__':
    unittest.main(verbosity=2)