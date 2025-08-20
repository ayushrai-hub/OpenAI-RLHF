# ideal_completion.py

class Node:
    def __init__(self, data, index):
        self.data = data
        self.index = index
        self.left = None
        self.right = None
        self.parent = None
        self.color = 'R'  # New nodes are initially red

class RedBlackTree:
    def __init__(self):
        self.NIL = Node(data=None, index=None)  
        self.NIL.color = 'B'  # Sentinel NIL node is black
        self.root = self.NIL

    def insert(self, data, index):
        new_node = Node(data, index)
        new_node.left = self.NIL
        new_node.right = self.NIL 
        parent = None
        node = self.root

        # Traverse the tree to find the correct position for the new node
        while node != self.NIL:
            parent = node
            if new_node.data < node.data or (new_node.data == node.data and new_node.index < node.index):
                node = node.left
            else:
                node = node.right

        # Attach the new node to the tree
        new_node.parent = parent
        if parent is None:  # Tree is empty
            self.root = new_node
        elif new_node.data < parent.data or (new_node.data == parent.data and new_node.index < parent.index):
            parent.left = new_node
        else:
            parent.right = new_node

        new_node.color = 'R'  # All new nodes start as red
        self.insert_fixup(new_node)  # Fix the tree to maintain Red-Black properties

    def insert_fixup(self, node):
        while node != self.root and node.parent.color == 'R':
            if node.parent == node.parent.parent.left:
                uncle = node.parent.parent.right
                if uncle.color == 'R':  # Case 1: Uncle is red
                    node.parent.color = 'B'
                    uncle.color = 'B'
                    node.parent.parent.color = 'R'
                    node = node.parent.parent
                else:  # Case 2 and 3: Uncle is black
                    if node == node.parent.right:
                        node = node.parent
                        self.left_rotate(node)
                    node.parent.color = 'B'
                    node.parent.parent.color = 'R'
                    self.right_rotate(node.parent.parent)
            else:
                uncle = node.parent.parent.left
                if uncle.color == 'R':  # Case 1: Uncle is red
                    node.parent.color = 'B'
                    uncle.color = 'B'
                    node.parent.parent.color = 'R'
                    node = node.parent.parent
                else:  # Case 2 and 3: Uncle is black
                    if node == node.parent.left:
                        node = node.parent
                        self.right_rotate(node)
                    node.parent.color = 'B'
                    node.parent.parent.color = 'R'
                    self.left_rotate(node.parent.parent)
        self.root.color = 'B'  # Ensure the root is always black

    def left_rotate(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:  # x was the root
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def right_rotate(self, y):
        x = y.left
        y.left = x.right
        if x.right != self.NIL:
            x.right.parent = y
        x.parent = y.parent
        if y.parent is None:  # y was the root
            self.root = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
        x.right = y
        y.parent = x

    def find_node(self, current_data, current_index, condition):
        """
        A generalized function to find a node based on a given condition.
        """
        node = self.root
        result = None
        while node != self.NIL:
            if condition(node, current_data, current_index):
                result = node
                node = node.left  # Continue searching for a better match
            else:
                node = node.right
        return result

    def find_next_larger(self, current_data, current_index):
        """
        Find the smallest element larger than or equal to current_data.
        """
        return self.find_node(
            current_data,
            current_index,
            lambda node, data, index: node.data > data or (node.data == data and node.index > index)
        )

    def find_next_smaller(self, current_data, current_index):
        """
        Find the largest element smaller than or equal to current_data.
        """
        return self.find_node(
            current_data,
            current_index,
            lambda node, data, index: node.data < data or (node.data == data and node.index > index)
        )

def relay_sheets_to_last_student(M, B):
    if M == 0:  # No students, no sheets reach the last student
        return 0
    if M == 1:  # Only one student, all sheets reach the last student
        return 1

    rb_tree = RedBlackTree()
    count = 0

    # Insert all students' data into the Red-Black Tree
    for i in range(M):
        rb_tree.insert(B[i], i)

    # Simulate the passing of sheets
    for i in range(M):
        steps = 0
        current = i
        current_data = B[i]
        current_index = i

        while current < M - 1:
            steps += 1
            if steps % 2 == 1:  # Odd step: find the next larger value
                candidate = rb_tree.find_next_larger(current_data, current_index)
            else:  # Even step: find the next smaller value
                candidate = rb_tree.find_next_smaller(current_data, current_index)

            # Stop if no valid candidate exists or we move backward
            if candidate is None or candidate.index <= current:
                break

            # Update the current position to the candidate's position
            current_data = candidate.data
            current_index = candidate.index
            current = current_index

        # If the last student (index M-1) is reached, increment the count
        if current == M - 1:
            count += 1

    return count