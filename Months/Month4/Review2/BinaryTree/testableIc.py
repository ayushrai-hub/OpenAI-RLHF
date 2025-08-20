class TreeIsEmptyError(Exception):
    pass
class Element:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
class BinaryTree:
    def __init__(self):
        self.root = None
    def isTreeEmpty(self):
        return self.root is None
    def add(self, val):
        self.root = self._add(self.root, val)
    def _add(self, node, val):
        if node is None:
            node = Element(val)
        elif val < node.data:
            node.left = self._add(node.left, val)
        elif val > node.data:
            node.right = self._add(node.right, val)
        else:
            pass
        return node
    def addIterative(self, val):
        current = self.root
        parent = None
        while current is not None:
            parent = current
            if val < current.data:
                current = current.left
            elif val > current.data:
                current = current.right
            else:
                return
        newnode = Element(val)
        if parent is None:
            self.root = newnode
        elif val < parent.data:
            parent.left = newnode
        else:
            parent.right = newnode
    def find(self, val):
        return self._find(self.root, val) is not None
    def _find(self, node, val):
        if node is None:
            return None
        if val < node.data:
            return self._find(node.left, val)
        if val > node.data:
            return self._find(node.right, val)
        return node
    def findIteratively(self, val):
        current = self.root
        while current is not None:
            if val < current.data:
                current = current.left
            elif val > current.data:
                current = current.right
            else:
                return True
        return False
    def remove(self, val):
        self.root = self._remove(self.root, val)
    def _remove(self, node, val):
        if node is None:
            return node
        if val < node.data:
            node.left = self._remove(node.left, val)
        elif val > node.data:
            node.right = self._remove(node.right, val)
        else:
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            succ = self._min_value_node(node.right)
            node.data = succ.data
            node.right = self._remove(node.right, succ.data)
        return node
    def _min_value_node(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current
    def find_min_iter(self):
        if self.isTreeEmpty():
            raise TreeIsEmptyError("Tree is empty")
        current = self.root
        while current.left is not None:
            current = current.left
        return current.data
    def find_min(self):
        if self.isTreeEmpty():
            raise TreeIsEmptyError("Tree is empty")
        return self._find_min(self.root)
    def _find_min(self, node):
        if node.left is None:
            return node.data
        return self._find_min(node.left)
    def find_max_iter(self):
        if self.isTreeEmpty():
            raise TreeIsEmptyError("Tree is empty")
        current = self.root
        while current.right is not None:
            current = current.right
        return current.data
    def find_max(self):
        if self.isTreeEmpty():
            raise TreeIsEmptyError("Tree is empty")
        return self._find_max(self.root)
    def _find_max(self, node):
        if node.right is None:
            return node.data
        return self._find_max(node.right)
    def find_second_min(self):
        if self.isTreeEmpty():
            raise TreeIsEmptyError("Tree is empty")
        return self._find_second_min(self.root)
    def _find_second_min(self, node):
        current = node
        parent = None
        while current.left is not None:
            parent = current
            current = current.left
        if current.right is not None:
            return self._find_min(current.right)
        return parent.data if parent else None
    def find_second_max(self):
        if self.isTreeEmpty():
            raise TreeIsEmptyError("Tree is empty")
        return self._find_second_max(self.root)
    def _find_second_max(self, node):
        current = node
        parent = None
        while current.right is not None:
            parent = current
            current = current.right
        if current.left is not None:
            return self._find_max(current.left)
        return parent.data if parent else None
    def treeHeight(self):
        return self._treeHeight(self.root)
    def _treeHeight(self, node):
        if node is None:
            return -1
        return 1 + max(self._treeHeight(node.left), self._treeHeight(node.right))
    def preorder(self):
        result = []
        self._preorder(self.root, result)
        return result
    def _preorder(self, node, result):
        if node:
            result.append(node.data)
            self._preorder(node.left, result)
            self._preorder(node.right, result)
    def inorder(self):
        result = []
        self._inorder(self.root, result)
        return result
    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.data)
            self._inorder(node.right, result)
    def postorder(self):
        result = []
        self._postorder(self.root, result)
        return result
    def _postorder(self, node, result):
        if node:
            self._postorder(node.left, result)
            self._postorder(node.right, result)
            result.append(node.data)
    def left_view(self):
        result = []
        self._left_view(self.root, 0, result)
        return result
    def _left_view(self, node, level, result):
        if node:
            if level == len(result):
                result.append(node.data)
            self._left_view(node.left, level + 1, result)
            self._left_view(node.right, level + 1, result)
    def show(self):
        self._show(self.root, 0)
        print()
    def _show(self, node, depth):
        if node is None:
            return
        self._show(node.right, depth + 1)
        print()
        for i in range(depth):
            print("    ", end='')
        print(node.data)
        self._show(node.left, depth + 1)
if __name__ == "__main__":
    binary_tree = BinaryTree()
    while True:
        option = int(input("Enter your option: "))
        if option == 1:
            binary_tree.show()
        elif option == 2:
            val = int(input("Enter the element to be found: "))
            if binary_tree.findIteratively(val):
                print("Element found")
            else:
                print("Element not found")
        elif option == 3:
            val = int(input("Enter the element to be found: "))
            if binary_tree.find(val):
                print("Element found")
            else:
                print("Element not found")
        elif option == 4:
            val = int(input("Enter the element to be added: "))
            binary_tree.addIterative(val)
        elif option == 5:
            val = int(input("Enter the element to be added: "))
            binary_tree.add(val)
        elif option == 6:
            print("Second smallest:", binary_tree.find_second_min())
            print("Second largest:", binary_tree.find_second_max())
        elif option == 7:
            val = int(input("Enter the element to be removed: "))
            binary_tree.remove(val)
        elif option == 8:
            print("Minimum element (Iterative):", binary_tree.find_min_iter())
        elif option == 9:
            print("Minimum element (Recursive):", binary_tree.find_min())
        elif option == 10:
            print("Maximum element (Iterative):", binary_tree.find_max_iter())
        elif option == 11:
            print("Maximum element (Recursive):", binary_tree.find_max())
        elif option == 12:
            print("Preorder Traversal:", binary_tree.preorder())
        elif option == 13:
            print("Inorder Traversal:", binary_tree.inorder())
        elif option == 14:
            print("Postorder Traversal:", binary_tree.postorder())
        elif option == 15:
            print("Tree Height:", binary_tree.treeHeight())
        elif option == 17:
            print("Left Side View of Tree:", binary_tree.left_view())
        elif option == 20:
            break
        else:
            print("Invalid option")
        print()
