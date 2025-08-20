import unittest
from io import StringIO
import sys
from unittest.mock import patch

# Assuming the above code is in a file named vault_system.py
from testable_ideal_solution import VaultEntryManager, SafeAccessController, process_vault_access

class TestVaultSystem(unittest.TestCase):
    def setUp(self):
        self.all_staff = ["EMP001", "EMP002", "EMP003", "EMP004"]
        self.cleared_staff = ["EMP001", "EMP002"]
        self.entry_manager = VaultEntryManager(self.cleared_staff, self.all_staff)

    def test_vault_entry_manager_initialization(self):
        """Test VaultEntryManager initialization and validation"""
        # Valid initialization
        manager = VaultEntryManager(self.cleared_staff, self.all_staff)
        self.assertEqual(manager.cleared_staff, set(self.cleared_staff))
        self.assertEqual(manager.all_staff, set(self.all_staff))
        
        # Test empty staff lists
        with self.assertRaises(ValueError):
            VaultEntryManager([], self.all_staff)
        with self.assertRaises(ValueError):
            VaultEntryManager(self.cleared_staff, [])
            
        # Test cleared staff > all staff
        with self.assertRaises(ValueError):
            VaultEntryManager(["EMP001", "EMP002", "EMP003"], ["EMP001", "EMP002"])

    def test_allow_entry(self):
        """Test entry permission validation"""
        # Test valid cleared staff
        self.entry_manager.allow_entry("EMP001")
        self.assertTrue(self.entry_manager.entry_allowed)
        
        # Test invalid staff ID
        with self.assertRaises(Exception) as context:
            self.entry_manager.allow_entry("INVALID")
        self.assertIn("invalid", str(context.exception))
        
        # Test unauthorized staff
        with self.assertRaises(Exception) as context:
            self.entry_manager.allow_entry("EMP003")
        self.assertIn("not cleared", str(context.exception))

    def test_close_entry(self):
        """Test entry closure"""
        self.entry_manager.allow_entry("EMP001")
        self.assertTrue(self.entry_manager.entry_allowed)
        self.entry_manager.close_entry()
        self.assertFalse(self.entry_manager.entry_allowed)

    def test_safe_access_controller(self):
        """Test SafeAccessController context manager"""
        # Test successful entry
        controller = SafeAccessController("EMP001", self.entry_manager)
        with controller as c:
            self.assertTrue(c.entry_granted)
            
        # Test failed entry
        controller = SafeAccessController("EMP003", self.entry_manager)
        with controller as c:
            self.assertFalse(c.entry_granted)

    def test_execute_task(self):
        """Test task execution"""
        controller = SafeAccessController("EMP001", self.entry_manager)
        
        # Capture stdout to verify output
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with controller:
            controller.execute_task("Check vault")
            
        sys.stdout = sys.__stdout__
        self.assertIn("Cleared Entry for EMP001", captured_output.getvalue())
        self.assertIn("Check vault", captured_output.getvalue())

class TestProcessVaultAccess(unittest.TestCase):
    @patch('builtins.input')
    def test_process_vault_access_valid_input(self, mock_input):
        """Test process_vault_access with valid input"""
        # Mock input values
        inputs = [
            "4",                    # n (total staff)
            "EMP001 EMP002 EMP003 EMP004",  # all staff
            "2",                    # g (cleared staff)
            "EMP001 EMP002",       # cleared staff
            "2",                    # q (requests)
            "EMP001",              # request 1 staff
            "Check safe",          # request 1 task
            "EMP003",              # request 2 staff
            "Deposit money"        # request 2 task
        ]
        mock_input.side_effect = inputs
        
        # Capture stdout to verify output
        captured_output = StringIO()
        sys.stdout = captured_output
        
        process_vault_access()
        
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        # Verify expected output
        self.assertIn("Cleared Entry for EMP001", output)
        self.assertIn("Check safe", output)
        self.assertIn("Unauthorized entry", output)
        self.assertIn("not cleared for vault access", output)

    @patch('builtins.input')
    def test_process_vault_access_invalid_input(self, mock_input):
        """Test process_vault_access with invalid input"""
        test_cases = [
            # Invalid n (total staff)
            (["0"], "Total staff count must be at least 1"),
            # Invalid g (cleared staff)
            (["2", "EMP001 EMP002", "3"], "Cleared staff count must be between"),
            # Invalid q (requests)
            (["2", "EMP001 EMP002", "1", "EMP001", "11"], "Number of requests must be between"),
        ]
        
        for inputs, expected_error in test_cases:
            mock_input.side_effect = inputs
            with self.assertRaises(ValueError) as context:
                process_vault_access()
            self.assertIn(expected_error, str(context.exception))

if __name__ == '__main__':
    unittest.main(verbosity=2)