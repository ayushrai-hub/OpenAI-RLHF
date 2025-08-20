
import unittest
from ideal_completion import BinaryTree, TreeIsEmptyError

class TestBinaryTree(unittest.TestCase):

    def setUp(self):
        self.tree = BinaryTree()
        # Inserting elements into the tree
        elements = [50, 30, 70, 20, 40, 60, 80]
        for elem in elements:
            self.tree.add(elem)

    def test_find(self):
        # Test if find method works (recursive)
        self.assertTrue(self.tree.find(70))
        self.assertFalse(self.tree.find(100))

    def test_find_iteratively(self):
        # Test if findIteratively method works
        self.assertTrue(self.tree.findIteratively(30))
        self.assertFalse(self.tree.findIteratively(99))

    def test_add_and_find_min(self):
        # Test adding elements and finding minimum (recursive)
        self.assertEqual(self.tree.find_min(), 20)  # Minimum of initial elements
        self.tree.add(10)
        self.assertEqual(self.tree.find_min(), 10)

    def test_add_iterative_and_find_max(self):
        # Test adding elements iteratively and finding maximum (iterative)
        self.assertEqual(self.tree.find_max_iter(), 80)
        self.tree.addIterative(90)
        self.assertEqual(self.tree.find_max_iter(), 90)

    def test_remove(self):
        # Test removing elements
        self.tree.remove(70)
        self.assertFalse(self.tree.find(70))
        self.tree.remove(20)
        self.assertFalse(self.tree.find(20))
        # Remove a non-existent element
        self.tree.remove(100)  # Should print "100  not found"

    def test_tree_height(self):
        # Test tree height
        self.assertEqual(self.tree.treeHeight(), 2)
        # Add more elements to increase height
        self.tree.add(5)
        self.assertEqual(self.tree.treeHeight(), 3)

    def test_traversals(self):
        # Test inorder traversal
        self.assertEqual(self.tree.inorder(), [20, 30, 40, 50, 60, 70, 80])
        # Test preorder traversal
        self.assertEqual(self.tree.preorder(), [50, 30, 20, 40, 70, 60, 80])
        # Test postorder traversal
        self.assertEqual(self.tree.postorder(), [20, 40, 30, 60, 80, 70, 50])

    def test_find_second_min_and_max(self):
        # Test finding second minimum and maximum
        self.assertEqual(self.tree.find_second_min(), 30)
        self.assertEqual(self.tree.find_second_max(), 70)
        # Remove elements to change second min and max
        self.tree.remove(20)
        self.assertEqual(self.tree.find_second_min(), 40)
        self.tree.remove(80)
        self.assertEqual(self.tree.find_second_max(), 60)

    def test_empty_tree_exceptions(self):
        empty_tree = BinaryTree()
        with self.assertRaises(TreeIsEmptyError):
            empty_tree.find_min()
        with self.assertRaises(TreeIsEmptyError):
            empty_tree.find_max()
        with self.assertRaises(TreeIsEmptyError):
            empty_tree.find_min_iter()
        with self.assertRaises(TreeIsEmptyError):
            empty_tree.find_max_iter()

    def test_left_view(self):
        # Test left view of the tree
        self.assertEqual(self.tree.left_view(), [50, 30, 20])

if __name__ == "__main__":
    unittest.main(verbosity=2)
