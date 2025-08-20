import unittest
from io import StringIO
from testableIC import VaultEntryManager, process_vault_access, SafeAccessController
class TestVaultSystem(unittest.TestCase):
    def setUp(self):
        self.all_staff = ["EMP001", "EMP002", "EMP003", "EMP004"]
        self.cleared_staff = ["EMP001", "EMP002"]
        self.entry_manager = VaultEntryManager(self.cleared_staff, self.all_staff)

    # Test VaultEntryManager initialization and validation
    def test_vault_entry_manager_initialization(self):
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

    # Test entry permission validation
    def test_allow_entry(self):
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

    # Test entry closure
    def test_close_entry(self):
        self.entry_manager.allow_entry("EMP001")
        self.assertTrue(self.entry_manager.entry_allowed)
        self.entry_manager.close_entry()
        self.assertFalse(self.entry_manager.entry_allowed)

    # Test SafeAccessController context manager
    def test_safe_access_controller(self):
        # Test successful entry
        controller = SafeAccessController("EMP001", self.entry_manager)
        with controller as c:
            self.assertTrue(c.entry_granted)
            
        # Test failed entry
        controller = SafeAccessController("EMP003", self.entry_manager)
        with controller as c:
            self.assertFalse(c.entry_granted)

    # Test task execution with return value
    def test_execute_task(self):
        controller = SafeAccessController("EMP001", self.entry_manager)
        
        with controller:
            result = controller.execute_task("Check vault")
            self.assertEqual(result, f"Cleared Entry for EMP001. Executed task: Check vault")

    # Test process_vault_access with input stream
    def test_process_vault_access(self):
        # Test valid input case
        input_data = StringIO(
            "4\n"  # n (total staff)
            "EMP001 EMP002 EMP003 EMP004\n"  # all staff
            "2\n"  # g (cleared staff)
            "EMP001 EMP002\n"  # cleared staff
            "2\n"  # q (requests)
            "EMP001\n"  # request 1 staff
            "Check safe\n"  # request 1 task
            "EMP003\n"  # request 2 staff
            "Deposit money\n"  # request 2 task
        )
        
        output = StringIO()
        process_vault_access(input_data, output)
        
        result = output.getvalue()
        self.assertIn("Cleared Entry for EMP001", result)
        self.assertIn("Check safe", result)
        self.assertIn("Unauthorized entry", result)
        
        # Test invalid input cases
        test_cases = [
            (StringIO("0\n"), "Total staff count must be at least 1"),
            (StringIO("2\nEMP001 EMP002\n3\n"), "Cleared staff count must be between"),
            (StringIO("2\nEMP001 EMP002\n1\nEMP001\n11\n"), "Number of requests must be between"),
        ]
        
        for input_stream, expected_error in test_cases:
            with self.assertRaises(ValueError) as context:
                process_vault_access(input_stream, StringIO())
            self.assertIn(expected_error, str(context.exception))

if __name__ == '__main__':
    unittest.main(verbosity=2)