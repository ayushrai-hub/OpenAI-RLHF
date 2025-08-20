import unittest
import execjs
import os

class TestTaskSlice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Read the JavaScript code from 'ideal_completion.js'
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'ideal_completion.js')), 'r') as f:
            cls.js_code = f.read()

        # Compile the JavaScript code
        cls.ctx = execjs.compile(cls.js_code)

    def test_addTask(self):
        """Test adding a new task."""
        initial_state = []
        new_task = {
            'id': 1,
            'title': 'Test Task',
            'description': 'A task',
            'dueDate': '2023-12-31',
            'priority': 'High',
            'status': 'Ongoing'
        }
        action = self.ctx.call('addTask', new_task)
        new_state = self.ctx.call('reducer', initial_state, action)
        expected_state = [new_task]
        self.assertEqual(new_state, expected_state)

    def test_updateTask(self):
        """Test updating an existing task."""
        initial_state = [
            {'id': 1, 'title': 'Old Title', 'description': 'Desc', 'dueDate': '2023-12-31', 'priority': 'Medium', 'status': 'Ongoing'}
        ]
        updated_task = {
            'id': 1,
            'title': 'New Title',
            'description': 'Updated Desc',
            'dueDate': '2023-12-25',
            'priority': 'High',
            'status': 'Done'
        }
        action = self.ctx.call('updateTask', updated_task)
        new_state = self.ctx.call('reducer', initial_state, action)
        expected_state = [updated_task]
        self.assertEqual(new_state, expected_state)

    def test_deleteTask(self):
        """Test deleting a task by ID."""
        initial_state = [
            {'id': 1, 'title': 'Task 1'},
            {'id': 2, 'title': 'Task 2'},
            {'id': 3, 'title': 'Task 3'}
        ]
        action = self.ctx.call('deleteTask', 2)
        new_state = self.ctx.call('reducer', initial_state, action)
        expected_state = [
            {'id': 1, 'title': 'Task 1'},
            {'id': 3, 'title': 'Task 3'}
        ]
        self.assertEqual(new_state, expected_state)

    def test_add_duplicate_task(self):
        """Test adding a task with a duplicate ID."""
        initial_state = [{'id': 1, 'title': 'Task 1'}]
        new_task = {'id': 1, 'title': 'Duplicate Task'}
        action = self.ctx.call('addTask', new_task)
        new_state = self.ctx.call('reducer', initial_state, action)
        expected_state = [
            {'id': 1, 'title': 'Task 1'},
            {'id': 1, 'title': 'Duplicate Task'}
        ]
        self.assertEqual(new_state, expected_state)

    def test_update_non_existent_task(self):
        """Test updating a task that does not exist."""
        initial_state = [{'id': 1, 'title': 'Task 1'}]
        updated_task = {'id': 2, 'title': 'Non-Existent Task'}
        action = self.ctx.call('updateTask', updated_task)
        new_state = self.ctx.call('reducer', initial_state, action)
        expected_state = [{'id': 1, 'title': 'Task 1'}]
        self.assertEqual(new_state, expected_state)

    def test_delete_non_existent_task(self):
        """Test deleting a task that does not exist."""
        initial_state = [{'id': 1, 'title': 'Task 1'}]
        action = self.ctx.call('deleteTask', 2)
        new_state = self.ctx.call('reducer', initial_state, action)
        expected_state = [{'id': 1, 'title': 'Task 1'}]
        self.assertEqual(new_state, expected_state)

    def test_empty_state_initialization(self):
        """Test handling actions with an empty initial state."""
        initial_state = []
        new_task = {'id': 1, 'title': 'New Task'}
        action = self.ctx.call('addTask', new_task)
        new_state = self.ctx.call('reducer', initial_state, action)
        expected_state = [{'id': 1, 'title': 'New Task'}]
        self.assertEqual(new_state, expected_state)

    def test_invalid_action_type(self):
        """Test handling of an invalid action type."""
        initial_state = [{'id': 1, 'title': 'Task 1'}]
        action = {'type': 'INVALID_ACTION', 'payload': None}
        new_state = self.ctx.call('reducer', initial_state, action)
        expected_state = [{'id': 1, 'title': 'Task 1'}]
        self.assertEqual(new_state, expected_state)

if __name__ == '__main__':
    unittest.main(verbosity=2)
