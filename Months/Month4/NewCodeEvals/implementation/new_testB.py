import unittest
from ideal_completion import BinaryTree, TreeIsEmptyError

class TestBinaryTree(unittest.TestCase):

    def setUp(self):
        self.tree = BinaryTree()
        # Inserting elements into the tree
        elements = [50, 30, 70, 20, 40, 60, 80]
        for elem in elements:
            self.tree.add(elem)

    def test_is_tree_empty(self):
        # Test empty tree check
        empty_tree = BinaryTree()
        self.assertTrue(empty_tree.isTreeEmpty())
        empty_tree.add(1)
        self.assertFalse(empty_tree.isTreeEmpty())

    def test_find(self):
        # Test if find method works (recursive)
        self.assertTrue(self.tree.find(70))
        self.assertFalse(self.tree.find(100))
        # Test with edge cases
        self.assertFalse(self.tree.find(float('-inf')))
        self.assertFalse(self.tree.find(float('inf')))

    def test_find_iteratively(self):
        # Test if findIteratively method works
        self.assertTrue(self.tree.findIteratively(30))
        self.assertFalse(self.tree.findIteratively(99))
        # Test with boundary cases
        self.assertFalse(self.tree.findIteratively(float('-inf')))
        self.assertFalse(self.tree.findIteratively(float('inf')))

    def test_add_and_find_min(self):
        # Test adding elements and finding minimum (recursive)
        self.assertEqual(self.tree.find_min(), 20)  # Minimum of initial elements
        self.tree.add(10)
        self.assertEqual(self.tree.find_min(), 10)
        # Test with very small values
        self.tree.add(-100)
        self.assertEqual(self.tree.find_min(), -100)

    def test_add_iterative_and_find_max(self):
        # Test adding elements iteratively and finding maximum (iterative)
        self.assertEqual(self.tree.find_max_iter(), 80)
        self.tree.addIterative(90)
        self.assertEqual(self.tree.find_max_iter(), 90)
        # Test with very large values
        self.tree.addIterative(1000)
        self.assertEqual(self.tree.find_max_iter(), 1000)

    def test_complex_tree_operations(self):
        # Build a more complex tree
        complex_tree = BinaryTree()
        elements = [50, 30, 70, 20, 40, 60, 80, 35, 45, 55, 65]
        for elem in elements:
            complex_tree.add(elem)
        
        # Test removal of node with two children
        complex_tree.remove(30)
        self.assertFalse(complex_tree.find(30))
        # Verify tree structure remains valid
        self.assertTrue(complex_tree.find(35))
        self.assertEqual(complex_tree.inorder(), 
                        [20, 35, 40, 45, 50, 55, 60, 65, 70, 80])

    def test_remove(self):
        # Test removing elements
        self.tree.remove(70)
        self.assertFalse(self.tree.find(70))
        self.tree.remove(20)
        self.assertFalse(self.tree.find(20))
        # Remove a non-existent element
        self.tree.remove(100)  # Should print "100  not found"
        # Test removing root
        self.tree.remove(50)
        self.assertFalse(self.tree.find(50))
        # Verify tree structure is still valid
        self.assertEqual(self.tree.inorder(), [30, 40, 60, 80])

    def test_tree_height(self):
        # Test tree height
        self.assertEqual(self.tree.treeHeight(), 2)
        # Add more elements to increase height
        self.tree.add(5)
        self.assertEqual(self.tree.treeHeight(), 3)
        # Test height of empty tree
        empty_tree = BinaryTree()
        self.assertEqual(empty_tree.treeHeight(), -1)

    def test_traversals(self):
        # Test inorder traversal
        self.assertEqual(self.tree.inorder(), [20, 30, 40, 50, 60, 70, 80])
        # Test preorder traversal
        self.assertEqual(self.tree.preorder(), [50, 30, 20, 40, 70, 60, 80])
        # Test postorder traversal
        self.assertEqual(self.tree.postorder(), [20, 40, 30, 60, 80, 70, 50])
        # Test traversals on empty tree
        empty_tree = BinaryTree()
        self.assertEqual(empty_tree.inorder(), [])
        self.assertEqual(empty_tree.preorder(), [])
        self.assertEqual(empty_tree.postorder(), [])

    def test_find_second_min_and_max(self):
        # Test finding second minimum and maximum
        self.assertEqual(self.tree.find_second_min(), 30)
        self.assertEqual(self.tree.find_second_max(), 70)
        # Remove elements to change second min and max
        self.tree.remove(20)
        self.assertEqual(self.tree.find_second_min(), 40)
        self.tree.remove(80)
        self.assertEqual(self.tree.find_second_max(), 60)
        # Test with single node tree
        single_tree = BinaryTree()
        single_tree.add(1)
        self.assertIsNone(single_tree.find_second_min())
        self.assertIsNone(single_tree.find_second_max())

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
        # Test left view of empty tree
        empty_tree = BinaryTree()
        self.assertEqual(empty_tree.left_view(), [])
        # Test left view of single node tree
        single_tree = BinaryTree()
        single_tree.add(1)
        self.assertEqual(single_tree.left_view(), [1])

    def test_bottom_and_top_view(self):
        # Test bottom view
        self.assertEqual(self.tree.bottom_view(), [20, 30, 60, 70, 80])
        # Test top view
        self.assertEqual(self.tree.top_view(), [20, 30, 50, 70, 80])
        
        # Test with empty tree
        empty_tree = BinaryTree()
        self.assertEqual(empty_tree.bottom_view(), [])
        self.assertEqual(empty_tree.top_view(), [])
        
        # Test with single node
        single_tree = BinaryTree()
        single_tree.add(1)
        self.assertEqual(single_tree.bottom_view(), [1])
        self.assertEqual(single_tree.top_view(), [1])
        
        # Test with unbalanced tree
        unbalanced_tree = BinaryTree()
        elements = [50, 40, 30, 20, 10]  # Left-heavy tree
        for elem in elements:
            unbalanced_tree.add(elem)
        self.assertEqual(unbalanced_tree.bottom_view(), [10, 20, 30, 40, 50])
        self.assertEqual(unbalanced_tree.top_view(), [10, 20, 30, 40, 50])

    def test_find_pairs_with_sum(self):
        # Test normal case
        self.assertEqual(self.tree.find_pairs_with_sum(100), [(20, 80), (30, 70), (40, 60)])
        
        # Test when no pairs exist
        self.assertEqual(self.tree.find_pairs_with_sum(1000), [])
        
        # Test with empty tree
        empty_tree = BinaryTree()
        self.assertEqual(empty_tree.find_pairs_with_sum(10), [])
        
        # Test with single node
        single_tree = BinaryTree()
        single_tree.add(5)
        self.assertEqual(single_tree.find_pairs_with_sum(10), [])

    def test_count_subtrees(self):
        # Test normal case
        self.assertEqual(self.tree.count_subtrees(), 7)  # Total nodes in initial tree
        
        # Test empty tree
        empty_tree = BinaryTree()
        self.assertEqual(empty_tree.count_subtrees(), 0)
        
        # Test single node
        single_tree = BinaryTree()
        single_tree.add(1)
        self.assertEqual(single_tree.count_subtrees(), 1)
        
        # Test complex tree
        complex_tree = BinaryTree()
        elements = [50, 30, 70, 20, 40, 60, 80, 35, 45]
        for elem in elements:
            complex_tree.add(elem)
        self.assertEqual(complex_tree.count_subtrees(), 9)

    def test_depth_of_node(self):
        # Test depths at different levels
        self.assertEqual(self.tree.depth_of_node(50), 0)  # root
        self.assertEqual(self.tree.depth_of_node(30), 1)
        self.assertEqual(self.tree.depth_of_node(20), 2)
        
        # Test non-existent node
        self.assertEqual(self.tree.depth_of_node(999), -1)
        
        # Test with empty tree
        empty_tree = BinaryTree()
        self.assertEqual(empty_tree.depth_of_node(1), -1)
        
        # Test with single node
        single_tree = BinaryTree()
        single_tree.add(1)
        self.assertEqual(single_tree.depth_of_node(1), 0)

    def test_complex_tree_restructuring(self):
        # Create a more complex tree
        complex_tree = BinaryTree()
        elements = [50, 30, 70, 20, 40, 60, 80, 35, 45, 55, 65, 75, 85]
        for elem in elements:
            complex_tree.add(elem)
        
        # Test multiple removals and additions
        complex_tree.remove(30)  # Remove node with two children
        complex_tree.remove(70)  # Remove another node with two children
        complex_tree.add(42)
        complex_tree.add(58)
        
        # Verify tree structure remains valid
        self.assertTrue(complex_tree.find(42))
        self.assertTrue(complex_tree.find(58))
        self.assertFalse(complex_tree.find(30))
        self.assertFalse(complex_tree.find(70))
        
        # Verify traversal order is still correct
        expected_inorder = [20, 35, 40, 42, 45, 50, 55, 58, 60, 65, 75, 80, 85]
        self.assertEqual(complex_tree.inorder(), expected_inorder)

    def test_duplicate_handling(self):
        # Attempt to add duplicates
        original_size = len(self.tree.inorder())
        self.tree.add(50)  # Duplicate root
        self.tree.add(30)  # Duplicate internal node
        self.tree.add(20)  # Duplicate leaf
        
        # Verify no duplicates were added
        self.assertEqual(len(self.tree.inorder()), original_size)
        
        # Verify tree structure remains valid
        expected_inorder = [20, 30, 40, 50, 60, 70, 80]
        self.assertEqual(self.tree.inorder(), expected_inorder)

if __name__ == "__main__":
    unittest.main(verbosity=2)

