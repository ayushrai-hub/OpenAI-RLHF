import unittest
from ideal_completion import RedBlackTree, relay_sheets_to_last_student, Node

class TestRedBlackTreeFunctionality(unittest.TestCase):

    def setUp(self):
        self.rb_tree = RedBlackTree()

    def test_initialization(self):
        # Test tree and NIL node initialization
        self.assertEqual(self.rb_tree.root, self.rb_tree.NIL)
        self.assertEqual(self.rb_tree.NIL.color, 'B')

    def test_insert(self):
        # Test basic insert functionality and root color property
        self.rb_tree.insert(10, 0)
        self.assertEqual(self.rb_tree.root.data, 10)
        self.assertEqual(self.rb_tree.root.color, 'B')

        self.rb_tree.insert(20, 1)
        self.assertEqual(self.rb_tree.root.right.data, 20)
        self.assertEqual(self.rb_tree.root.right.color, 'R')

        self.rb_tree.insert(5, 2)
        self.assertEqual(self.rb_tree.root.left.data, 5)
        self.assertEqual(self.rb_tree.root.left.color, 'R')

    def test_left_rotate(self):
        # Test the left rotation maintains tree structure and properties
        self.rb_tree.insert(10, 0)
        self.rb_tree.insert(5, 1)
        self.rb_tree.insert(20, 2)
        self.rb_tree.insert(15, 3)
        self.rb_tree.insert(25, 4)
        self.rb_tree.left_rotate(self.rb_tree.root.right)

        self.assertEqual(self.rb_tree.root.right.data, 25)
        self.assertEqual(self.rb_tree.root.right.left.data, 20)

    def test_right_rotate(self):
        # Test the right rotation maintains tree structure and properties
        self.rb_tree.insert(20, 0)
        self.rb_tree.insert(10, 1)
        self.rb_tree.insert(30, 2)
        self.rb_tree.insert(5, 3)
        self.rb_tree.insert(15, 4)
        self.rb_tree.right_rotate(self.rb_tree.root.left)

        self.assertEqual(self.rb_tree.root.left.data, 5)
        self.assertEqual(self.rb_tree.root.left.right.data, 10)

    def test_relay_sheets_provided_input(self):
        # Test relay sheets with the provided input
        C = [34, 67, 43, 78, 89]
        result = relay_sheets_to_last_student(len(C), C)
        self.assertEqual(result, 2)

    def test_relay_sheets_single_student(self):
        # Test relay functionality with only one student
        C = [42]
        result = relay_sheets_to_last_student(len(C), C)
        self.assertEqual(result, 1)

    def test_relay_sheets_all_possible_transfers(self):
        # Test relay functionality with strictly increasing values
        C = [1, 2, 3, 4, 5]
        result = relay_sheets_to_last_student(len(C), C)
        self.assertEqual(result, 2)

    def test_relay_sheets_no_possible_transfers(self):
        # Test relay functionality with strictly decreasing values
        C = [100, 90, 80, 70, 60]
        result = relay_sheets_to_last_student(len(C), C)
        self.assertEqual(result, 1)

    def test_relay_sheets_alternating_values(self):
        # Test relay functionality with alternating values
        C = [50, 30, 60, 20, 70]
        result = relay_sheets_to_last_student(len(C), C)
        self.assertEqual(result, 2)

    def test_empty_tree(self):
        # Test properties of an empty tree
        self.assertEqual(self.rb_tree.root, self.rb_tree.NIL)
        self.assertEqual(self.rb_tree.root.color, 'B')

    def test_sequential_inserts(self):
        # Test sequential inserts and check tree color property
        elements = [15, 6, 23, 5, 71, 50]
        for index, element in enumerate(elements):
            self.rb_tree.insert(element, index)
        self.assertNotEqual(self.rb_tree.root, self.rb_tree.NIL)
        self.assertEqual(self.rb_tree.root.color, 'B')

    def test_complex_rotation(self):
        # Test complex rotations within the tree
        values = [41, 20, 65, 11, 29, 50, 91, 32, 72]
        for index, value in enumerate(values):
            self.rb_tree.insert(value, index)
        self.assertEqual(self.rb_tree.root.data, 41)
        self.assertEqual(self.rb_tree.root.right.data, 65)
        self.assertTrue(self.rb_tree.root.left.color, 'R')

if __name__ == '__main__':
    unittest.main(verbosity=2)