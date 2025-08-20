# ideal_completion.py

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
            return Element(val)
        elif val < node.data:
            node.left = self._add(node.left, val)
        elif val > node.data:
            node.right = self._add(node.right, val)
        else:
            print(val, " already exists in the binary tree")
        return node

    def addIterative(self, val):
        newnode = Element(val)
        if self.root is None:
            self.root = newnode
            return
        current = self.root
        while True:
            if val < current.data:
                if current.left is None:
                    current.left = newnode
                    break
                current = current.left
            elif val > current.data:
                if current.right is None:
                    current.right = newnode
                    break
                current = current.right
            else:
                print(val, " already exists in the binary tree")
                break

    def find(self, val):
        return self._find(self.root, val) is not None

    def _find(self, node, val):
        if node is None:
            return None
        elif val < node.data:
            return self._find(node.left, val)
        elif val > node.data:
            return self._find(node.right, val)
        else:
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
            print(val, " not found")
            return None
        if val < node.data:
            node.left = self._remove(node.left, val)
        elif val > node.data:
            node.right = self._remove(node.right, val)
        else:
            if node.left is None:
                temp = node.right
                node = None
                return temp
            elif node.right is None:
                temp = node.left
                node = None
                return temp
            temp = self._min_value_node(node.right)
            node.data = temp.data
            node.right = self._remove(node.right, temp.data)
        return node

    def _min_value_node(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current

    def find_min(self):
        if self.isTreeEmpty():
            raise TreeIsEmptyError("Tree is empty")
        return self._find_min(self.root)

    def _find_min(self, node):
        if node.left is None:
            return node.data
        else:
            return self._find_min(node.left)

    def find_min_iter(self):
        if self.isTreeEmpty():
            raise TreeIsEmptyError("Tree is empty")
        current = self.root
        while current.left is not None:
            current = current.left
        return current.data

    def find_max(self):
        if self.isTreeEmpty():
            raise TreeIsEmptyError("Tree is empty")
        return self._find_max(self.root)

    def _find_max(self, node):
        if node.right is None:
            return node.data
        else:
            return self._find_max(node.right)

    def find_max_iter(self):
        if self.isTreeEmpty():
            raise TreeIsEmptyError("Tree is empty")
        current = self.root
        while current.right is not None:
            current = current.right
        return current.data

    def find_second_min(self):
        if self.isTreeEmpty():
            raise TreeIsEmptyError("Tree is empty")
        current = self.root
        prev = None
        while current.left is not None:
            prev = current
            current = current.left
        if current.right is not None:
            return self._find_min(current.right)
        elif prev is not None:
            return prev.data
        else:
            return None

    def find_second_max(self):
        if self.isTreeEmpty():
            raise TreeIsEmptyError("Tree is empty")
        current = self.root
        prev = None
        while current.right is not None:
            prev = current
            current = current.right
        if current.left is not None:
            return self._find_max(current.left)
        elif prev is not None:
            return prev.data
        else:
            return None

    def treeHeight(self):
        return self._treeHeight(self.root)

    def _treeHeight(self, node):
        if node is None:
            return -1
        else:
            return 1 + max(self._treeHeight(node.left), self._treeHeight(node.right))

    def inorder(self):
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.data)
            self._inorder(node.right, result)

    def preorder(self):
        result = []
        self._preorder(self.root, result)
        return result

    def _preorder(self, node, result):
        if node:
            result.append(node.data)
            self._preorder(node.left, result)
            self._preorder(node.right, result)

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
        max_level = [0]
        self._left_view(self.root, 1, max_level, result)
        return result

    def _left_view(self, node, level, max_level, result):
        if node is None:
            return
        if max_level[0] < level:
            result.append(node.data)
            max_level[0] = level
        self._left_view(node.left, level + 1, max_level, result)
        self._left_view(node.right, level + 1, max_level, result)

    def show(self):
        self._show(self.root, 0)
        print()

    def _show(self, node, depth):
        if node is None:
            return
        self._show(node.right, depth + 1)
        print()
        for _ in range(depth):
            print("    ", end='')
        print(node.data)
        self._show(node.left, depth + 1)

    def depth_of_node(self, val):
        return self._depth_of_node(self.root, val, 0)

    def _depth_of_node(self, node, val, depth):
        if node is None:
            return -1
        if node.data == val:
            return depth
        elif val < node.data:
            return self._depth_of_node(node.left, val, depth + 1)
        else:
            return self._depth_of_node(node.right, val, depth + 1)

    def find_pairs_with_sum(self, k):
        nodes_list = []
        self._inorder(self.root, nodes_list)
        left = 0
        right = len(nodes_list) - 1
        pairs = []
        while left < right:
            current_sum = nodes_list[left] + nodes_list[right]
            if current_sum == k:
                pairs.append((nodes_list[left], nodes_list[right]))
                left += 1
                right -= 1
            elif current_sum < k:
                left += 1
            else:
                right -= 1
        return pairs

    def count_subtrees(self):
        return self._count_subtrees(self.root)

    def _count_subtrees(self, node):
        if node is None:
            return 0
        return 1 + self._count_subtrees(node.left) + self._count_subtrees(node.right)

    def bottom_view(self):
        if not self.root:
            return []
        from collections import deque, OrderedDict
        queue = deque()
        hd_node = {}
        queue.append((self.root, 0))
        while queue:
            node, hd = queue.popleft()
            hd_node[hd] = node.data
            if node.left:
                queue.append((node.left, hd - 1))
            if node.right:
                queue.append((node.right, hd + 1))
        return [hd_node[key] for key in sorted(hd_node)]

    def top_view(self):
        if not self.root:
            return []
        from collections import deque, OrderedDict
        queue = deque()
        hd_node = {}
        queue.append((self.root, 0))
        while queue:
            node, hd = queue.popleft()
            if hd not in hd_node:
                hd_node[hd] = node.data
            if node.left:
                queue.append((node.left, hd - 1))
            if node.right:
                queue.append((node.right, hd + 1))
        return [hd_node[key] for key in sorted(hd_node)]