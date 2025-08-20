# ideal_completion.py
class RBTNode:
    def __init__(self, key, value, color='R'):
        self.key = key          # B[l] value
        self.value = value      # Student index l
        self.color = color      # 'R' for Red, 'B' for Black
        self.left = None
        self.right = None
        self.parent = None

class RBTree:
    def __init__(self):
        self.NIL_LEAF = RBTNode(None, None, 'B')  # Sentinel Node for NIL leaves
        self.root = self.NIL_LEAF

    def insert(self, key, value):
        new_node = RBTNode(key, value)
        self._insert_node(new_node)
        self._rebalance_tree(new_node)

    def _insert_node(self, node):
        node.left = self.NIL_LEAF
        node.right = self.NIL_LEAF
        node.parent = None

        if self.root == self.NIL_LEAF:
            self.root = node
            node.color = 'B'
            return

        current = self.root
        while True:
            if node.key < current.key:
                if current.left == self.NIL_LEAF:
                    current.left = node
                    node.parent = current
                    break
                else:
                    current = current.left
            elif node.key > current.key:
                if current.right == self.NIL_LEAF:
                    current.right = node
                    node.parent = current
                    break
                else:
                    current = current.right
            else:
                # If key already exists, keep the smallest index (earlier student)
                if node.value < current.value:
                    current.value = node.value
                break

    def _rebalance_tree(self, node):
        while node != self.root and node.parent.color == 'R':
            if node.parent == node.parent.parent.left:
                uncle = node.parent.parent.right
                if uncle.color == 'R':
                    node.parent.color = 'B'
                    uncle.color = 'B'
                    node.parent.parent.color = 'R'
                    node = node.parent.parent
                else:
                    if node == node.parent.right:
                        node = node.parent
                        self._rotate_left(node)
                    node.parent.color = 'B'
                    node.parent.parent.color = 'R'
                    self._rotate_right(node.parent.parent)
            else:
                uncle = node.parent.parent.left
                if uncle.color == 'R':
                    node.parent.color = 'B'
                    uncle.color = 'B'
                    node.parent.parent.color = 'R'
                    node = node.parent.parent
                else:
                    if node == node.parent.left:
                        node = node.parent
                        self._rotate_right(node)
                    node.parent.color = 'B'
                    node.parent.parent.color = 'R'
                    self._rotate_left(node.parent.parent)
        self.root.color = 'B'

    def _rotate_left(self, node):
        right_child = node.right
        node.right = right_child.left
        if right_child.left != self.NIL_LEAF:
            right_child.left.parent = node
        right_child.parent = node.parent
        if node.parent is None:
            self.root = right_child
        elif node == node.parent.left:
            node.parent.left = right_child
        else:
            node.parent.right = right_child
        right_child.left = node
        node.parent = right_child

    def _rotate_right(self, node):
        left_child = node.left
        node.left = left_child.right
        if left_child.right != self.NIL_LEAF:
            left_child.right.parent = node
        left_child.parent = node.parent
        if node.parent is None:
            self.root = left_child
        elif node == node.parent.right:
            node.parent.right = left_child
        else:
            node.parent.left = left_child
        left_child.right = node
        node.parent = left_child

    def find_min_ge(self, key):
        """Find the node with the smallest key >= given key."""
        node = self.root
        result = None
        while node != self.NIL_LEAF:
            if node.key >= key:
                result = node
                node = node.left
            else:
                node = node.right
        return result

    def find_max_le(self, key):
        """Find the node with the largest key <= given key."""
        node = self.root
        result = None
        while node != self.NIL_LEAF:
            if node.key <= key:
                result = node
                node = node.right
            else:
                node = node.left
        return result

    def search(self, key):
        """Search for a node with the given key."""
        node = self.root
        while node != self.NIL_LEAF:
            if key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
            else:
                return node
        return None

def relay_sheets_to_last_student(B):
    m = len(B)
    next_l = [[None, None] for _ in range(m)]  # next_l[k][0] for even, next_l[k][1] for odd

    tree_asc = RBTree()    # For odd instances: find min B[l] >= B[k]
    tree_desc = RBTree()   # For even instances: find max B[l] <= B[k]

    for k in reversed(range(m)):
        # Odd step (u is odd, p=1)
        node_asc = tree_asc.find_min_ge(B[k])
        if node_asc:
            next_l[k][1] = node_asc.value  # l index

        # Even step (u is even, p=0)
        node_desc = tree_desc.find_max_le(B[k])
        if node_desc:
            next_l[k][0] = node_desc.value  # l index

        # Insert into trees if key not present to maintain the smallest l
        if not tree_asc.search(B[k]):
            tree_asc.insert(B[k], k)
        if not tree_desc.search(B[k]):
            tree_desc.insert(B[k], k)

    # Initialize memoization table
    dp = [[None, None] for _ in range(m)]

    def can_reach(k, p):
        if k == m - 1:
            return True
        if dp[k][p] is not None:
            return dp[k][p]
        next_k = next_l[k][p]
        if next_k is None:
            dp[k][p] = False
            return False
        dp[k][p] = can_reach(next_k, 1 - p)
        return dp[k][p]

    # Count the number of answer sheets that can reach the last student
    count = 0
    for k in range(m):
        if can_reach(k, 1):  # Start with the first step being odd (u=1)
            count += 1
    return count