class RBTNode:
    def __init__(self, value, color='R'):
        self.value = value
        self.color = color  # 'R' for Red, 'B' for Black
        self.left = None
        self.right = None
        self.parent = None

class RBTree:
    def __init__(self):
        self.NIL_LEAF = RBTNode(None, 'B')  # Sentinel Node for NIL leaves
        self.root = self.NIL_LEAF

    def insert(self, value):
        new_node = RBTNode(value)
        self._insert_node(new_node)
        self._rebalance_tree(new_node)

    def _insert_node(self, node):
        if self.root == self.NIL_LEAF:
            self.root = node
            node.color = 'B'
            node.left = self.NIL_LEAF
            node.right = self.NIL_LEAF
            return

        current = self.root
        while True:
            if node.value < current.value:
                if current.left == self.NIL_LEAF:
                    current.left = node
                    node.parent = current
                    node.left = self.NIL_LEAF
                    node.right = self.NIL_LEAF
                    break
                else:
                    current = current.left
            else:
                if current.right == self.NIL_LEAF:
                    current.right = node
                    node.parent = current
                    node.left = self.NIL_LEAF
                    node.right = self.NIL_LEAF
                    break
                else:
                    current = current.right
    
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

    def find_next_larger(self, value):
        node = self.root
        next_larger = None
        while node != self.NIL_LEAF:
            if node.value > value:
                next_larger = node
                node = node.left
            else:
                node = node.right
        return next_larger

    def find_next_smaller(self, value):
        node = self.root
        next_smaller = None
        while node != self.NIL_LEAF:
            if node.value < value:
                next_smaller = node
                node = node.right
            else:
                node = node.left
        return next_smaller


def relay_sheets_to_last_student(C):
    p = len(C)
    rbt = RBTree()
    rbt.insert(C[-1])

    complete_sheets = 0  # Start counting already completed
    
    for i in range(p - 2, -1, -1):
        if i % 2 == 1:  # Odd step, find smallest greater element
            next_larger = rbt.find_next_larger(C[i])
            if next_larger:
                complete_sheets += 1
        else:  # Even step, find largest smaller element
            next_smaller = rbt.find_next_smaller(C[i])
            if next_smaller:
                complete_sheets += 1
        rbt.insert(C[i])

    return complete_sheets
