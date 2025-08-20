import unittest
from testableIc import *

class TestBinaryTree(unittest.TestCase):

    def setUp(self):
        """Set up a binary tree with predefined elements for testing."""
        self.tree = BinaryTree()
        elements = [20, 10, 30, 5, 15, 25, 35]
        for element in elements:
            self.tree.add(element)

    def test_is_tree_empty(self):
        """Test if the tree is not empty after adding elements."""
        self.assertFalse(self.tree.isTreeEmpty())

    def test_add_and_find_element(self):
        """Test adding a new element and finding it in the tree."""
        self.tree.add(40)
        self.assertTrue(self.tree.find(40))

    def test_find_element_iterative(self):
        """Test iterative search method to find an element."""
        self.assertTrue(self.tree.findIteratively(25))
        self.assertFalse(self.tree.findIteratively(50))

    def test_remove_element(self):
        """Test removing an element from the tree."""
        self.tree.remove(15)
        self.assertFalse(self.tree.find(15))

    def test_find_min_recursive(self):
        """Test finding the minimum element using recursion."""
        self.assertEqual(self.tree.find_min(), 5)

    def test_find_min_iterative(self):
        """Test finding the minimum element using iteration."""
        self.assertEqual(self.tree.find_min_iter(), 5)

    def test_find_max_recursive(self):
        """Test finding the maximum element using recursion."""
        self.assertEqual(self.tree.find_max(), 35)

    def test_find_max_iterative(self):
        """Test finding the maximum element using iteration."""
        self.assertEqual(self.tree.find_max_iter(), 35)

    def test_find_second_min(self):
        """Test finding the second minimum element in the tree."""
        self.assertEqual(self.tree.find_second_min(), 10)

    def test_find_second_max(self):
        """Test finding the second maximum element in the tree."""
        self.assertEqual(self.tree.find_second_max(), 30)

    def test_tree_height(self):
        """Test calculating the height of the tree."""
        self.assertEqual(self.tree.treeHeight(), 2)

    def test_preorder_traversal(self):
        """Test the preorder traversal of the tree."""
        self.assertEqual(self.tree.preorder(), [20, 10, 5, 15, 30, 25, 35])

    def test_inorder_traversal(self):
        """Test the inorder traversal of the tree."""
        self.assertEqual(self.tree.inorder(), [5, 10, 15, 20, 25, 30, 35])

    def test_postorder_traversal(self):
        """Test the postorder traversal of the tree."""
        self.assertEqual(self.tree.postorder(), [5, 15, 10, 25, 35, 30, 20])

    def test_left_view(self):
        """Test the left view of the tree."""
        self.assertEqual(self.tree.left_view(), [20, 10, 5])

    def test_find_pair_with_sum(self):
        """Test finding a pair of nodes that sum up to a given value."""
        self.assertEqual(self.tree.find_pair_with_sum(35), (5, 30))
        self.assertIsNone(self.tree.find_pair_with_sum(100))

    def test_top_view(self):
        """Test getting the top view of the tree."""
        self.assertEqual(self.tree.top_view(), [5, 10, 20, 30, 35])

    def test_bottom_view(self):
        """Test getting the bottom view of the tree."""
        self.assertEqual(self.tree.bottom_view(), [5, 10, 25, 30, 35])

if __name__ == '__main__':
    unittest.main(verbosity=2)