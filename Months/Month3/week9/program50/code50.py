#1. Identifying the Missing Number in an Integer Array (1-100)
def find_absent(arr):
    n = 100
    return n * (n + 1) // 2 - sum(arr)

# Example
print(find_absent([1, 2, 3, 4, 5]))  # Output will indicate the missing number

#2. Identifying the Repeated Number in an Array
def find_repeated(arr):
    seen = set()
    for num in arr:
        if num in seen:
            return num
        seen.add(num)

# Example
print(find_repeated([1, 2, 3, 4, 3]))  # Output: 3


#3. Identifying the Max and Min Numbers in an Unordered Array
def find_max_min(arr):
    return max(arr), min(arr)

# Example
print(find_max_min([3, 5, 1, 2, 4]))  # Output: (5, 1)


#4. Identifying All Pairs that Sum to a Specified Value
def find_value_pairs(arr, target):
    pairs = []
    seen = set()
    for num in arr:
        if target - num in seen:
            pairs.append((num, target - num))
        seen.add(num)
    return pairs

# Example
print(find_value_pairs([1, 2, 3, 4, 5], 6))  # Output: [(4, 2), (5, 1)]


#5. Identifying All Repeated Numbers in an Array
def find_all_repeats(arr):
    from collections import Counter
    return [item for item, count in Counter(arr).items() if count > 1]

# Example
print(find_all_repeats([1, 2, 3, 2, 4, 3]))  # Output: [2, 3]




#6. Eliminating Duplicates from an Array In-Place
def eliminate_duplicates(arr):
    return list(set(arr))

# Example
print(eliminate_duplicates([1, 2, 2, 3, 4, 4]))  # Output: [1, 2, 3, 4]




#7. Sorting an Integer Array Using the Quicksort
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

# Example
print(quicksort([3, 6, 8, 10, 1, 2, 1]))  # Output: [1, 1, 2, 3, 6, 8, 10]



#8. Removing Duplicates from an Array In-Place
def in_place_eliminate_duplicates(arr):
    i = 0
    while i < len(arr):
        if arr.count(arr[i]) > 1:
            arr.remove(arr[i])
        else:
            i += 1
    return arr

# Example
print(in_place_eliminate_duplicates([1, 2, 2, 3, 4, 4]))  # Output: [1, 3]


#9. Reversing an Array in Place in Python
def flip_array(arr):
    return arr[::-1]

# Example
print(flip_array([1, 2, 3, 4]))  # Output: [4, 3, 2, 1]


#10. Removing Duplicates from an Array Without Libraries
def manual_eliminate_duplicates(arr):
    result = []
    for num in arr:
        if num not in result:
            result.append(num)
    return result

# Example
print(manual_eliminate_duplicates([1, 2, 2, 3, 4, 4]))  # Output: [1, 2, 3, 4]


#Linked List Coding Challenges
#Below is a straightforward linked list class in Python:

#11
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None


#12. Finding the Middle Element of a Singly Linked List in One Pass

def locate_middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow.data

# Example: Assume linked list is created and head is the head node

#13. Verifying if a Linked List Has a Cycle and Locating the Start

def find_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            break
    if not fast or not fast.next:
        return None
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next
    return slow




#14. Reversing a Linked List

def flip_list(head):
    prev = None
    current = head
    while current:
        next_node = current.next
        current.next = prev
        prev = current
        current = next_node
    return prev

# Example: reversed_head = flip_list(head)

#15. How do you invert a singly linked list without using recursion
def reverse_list_iterative(head):
    prev = None
    current = head
    while current is not None:
        #store the next node
        next_node = current.next
        #Reverse the linked list
        current.next = prev
        #move prev and current one step forward
        prev = current
        current = next_node
    return prev

#16. Eliminating Repeated Nodes in an Unsorted Linked List

def remove_repeats_from_linkedlist(head):
    if not head:
        return
    current = head
    seen = set([current.data])
    while current.next:
        if current.next.data in seen:
            current.next = current.next.next
        else:
            seen.add(current.next.data)
            current = current.next
    return head


#17. Calculating the Length of a Singly Linked List
def list_length(head):
    count = 0
    current = head
    while current:
        count += 1
        current = current.next
    return count



#18. Locating the Third Node from the End in a Singly Linked List
def third_node_from_end(head):
    slow = fast = head
    for _ in range(2):
        if fast:
            fast = fast.next
    while fast and fast.next:
        slow = slow.next
        fast = fast.next
    return slow.data if slow else None



#19. Adding Two Linked Lists Using Stack
def sum_two_numbers(l1, l2):
    s1, s2 = [], []
    while l1:
        s1.append(l1.data)
        l1 = l1.next
    while l2:
        s2.append(l2.data)
        l2 = l2.next
    
    carry = 0
    result = None
    while s1 or s2 or carry:
        add = carry
        if s1:
            add += s1.pop()
        if s2:
            add += s2.pop()
        carry, val = divmod(add, 10)
        new_node = Node(val)
        new_node.next = result
        result = new_node
    return result





#String Coding Challenges
#19. Outputting Duplicate Characters from a String

def output_duplicates(s):
    from collections import Counter
    counter = Counter(s)
    return [char for char, count in counter.items() if count > 1]

# Example
print(output_duplicates("programming"))  # Output: ['r', 'g', 'm']



#20. Verifying if Two Strings are Anagrams
def check_anagrams(s1, s2):
    return sorted(s1) == sorted(s2)

# Example
print(check_anagrams("listen", "silent"))  # Output: True




#21. Printing the First Character That Isn't Repeated from a String
def first_non_repeat_char(s):
    from collections import Counter
    counter = Counter(s)
    for char in s:
        if counter[char] == 1:
            return char

# Example
print(first_non_repeat_char("programming"))  # Output: 'p'





#22. Inverting a String Using Recursion
def invert_string(s):
    if len(s) == 0:
        return s
    return s[-1] + invert_string(s[:-1])

# Example
print(invert_string("hello"))  # Output: 'olleh'



#23. Ensuring a String Only Includes Digits

def includes_only_digits(s):
    return s.isdigit()

# Example
print(includes_only_digits("12345"))  # Output: True




#24. Locate duplicate characters in a string
def find_duplicates(s):
    return [char for char in set(s) if s.count(char) > 1]

# 25. Count vowels and consonants in a string
def count_vowels_consonants(s):
    vowels = sum(1 for char in s.lower() if char in 'aeiou')
    consonants = sum(1 for char in s.lower() if char.isalpha() and char not in 'aeiou')
    return vowels, consonants

# 26. Count occurrences of a character in a string
def count_char(s, char):
    return s.count(char)

# 27. Find all permutations of a string
from itertools import permutations

def string_permutations(s):
    return [''.join(p) for p in permutations(s)]

# 28. Reverse words in a sentence without library methods
def reverse_words(sentence):
    words = sentence.split()
    return ' '.join(word[::-1] for word in words)

# 29. Check if two strings are rotations of each other
def are_rotations(s1, s2):
    return len(s1) == len(s2) and s2 in s1 + s1

# 30. Check if a string is a palindrome
def is_palindrome(s):
    return s == s[::-1]


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# 31. Initialize a binary search tree
class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, val):
        if not self.root:
            self.root = TreeNode(val)
        else:
            self._insert_recursive(self.root, val)

    def _insert_recursive(self, node, val):
        if val < node.val:
            if node.left is None:
                node.left = TreeNode(val)
            else:
                self._insert_recursive(node.left, val)
        else:
            if node.right is None:
                node.right = TreeNode(val)
            else:
                self._insert_recursive(node.right, val)

# 32. Preorder traversal (recursive)
def preorder_traversal(root):
    if root:
        print(root.val, end=' ')
        preorder_traversal(root.left)
        preorder_traversal(root.right)

# 33. Preorder traversal (iterative)
def preorder_traversal_iterative(root):
    if not root:
        return
    stack = [root]
    while stack:
        node = stack.pop()
        print(node.val, end=' ')
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)

# 34. Inorder traversal (recursive)
def inorder_traversal(root):
    if root:
        inorder_traversal(root.left)
        print(root.val, end=' ')
        inorder_traversal(root.right)

# 35. Inorder traversal (iterative)
def inorder_traversal_iterative(root):
    stack = []
    current = root
    while current or stack:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        print(current.val, end=' ')
        current = current.right

# 36. Postorder traversal (recursive)
def postorder_traversal(root):
    if root:
        postorder_traversal(root.left)
        postorder_traversal(root.right)
        print(root.val, end=' ')

# 37. Postorder traversal (iterative)
def postorder_traversal_iterative(root):
    if not root:
        return
    stack1, stack2 = [root], []
    while stack1:
        node = stack1.pop()
        stack2.append(node)
        if node.left:
            stack1.append(node.left)
        if node.right:
            stack1.append(node.right)
    while stack2:
        print(stack2.pop().val, end=' ')

# 38. Display all leaf nodes of a binary search tree
def display_leaf_nodes(root):
    if not root:
        return
    if not root.left and not root.right:
        print(root.val, end=' ')
    display_leaf_nodes(root.left)
    display_leaf_nodes(root.right)

# 39. Count leaf nodes in a binary tree
def count_leaf_nodes(root):
    if not root:
        return 0
    if not root.left and not root.right:
        return 1
    return count_leaf_nodes(root.left) + count_leaf_nodes(root.right)

# 40. Binary search in an array
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# 41. Bubble sort algorithm
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# 42. Iterative quicksort algorithm
def quicksort_iterative(arr):
    stack = [(0, len(arr) - 1)]
    while stack:
        low, high = stack.pop()
        if low < high:
            pivot = partition(arr, low, high)
            stack.append((low, pivot - 1))
            stack.append((pivot + 1, high))
    return arr

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

# 43. Insertion sort algorithm
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

# 44. Merge sort algorithm
def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr) // 2
        L = arr[:mid]
        R = arr[mid:]
        merge_sort(L)
        merge_sort(R)
        i = j = k = 0
        while i < len(L) and j < len(R):
            if L[i] < R[j]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1
        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1
        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1
    return arr

# 45. Bucket sort algorithm
def bucket_sort(arr):
    max_val = max(arr)
    size = max_val / len(arr)
    buckets = [[] for _ in range(len(arr))]
    for num in arr:
        i = int(num / size)
        if i != len(arr):
            buckets[i].append(num)
        else:
            buckets[len(arr) - 1].append(num)
    for i in range(len(arr)):
        insertion_sort(buckets[i])
    return [num for bucket in buckets for num in bucket]

# 46. Counting sort algorithm
def counting_sort(arr):
    max_val = max(arr)
    m = max_val + 1
    count = [0] * m
    for a in arr:
        count[a] += 1
    i = 0
    for a in range(m):
        for c in range(count[a]):
            arr[i] = a
            i += 1
    return arr

# 47. Radix sort algorithm
def radix_sort(arr):
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        counting_sort_for_radix(arr, exp)
        exp *= 10
    return arr

def counting_sort_for_radix(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10
    for i in range(n):
        index = arr[i] // exp
        count[index % 10] += 1
    for i in range(1, 10):
        count[i] += count[i - 1]
    i = n - 1
    while i >= 0:
        index = arr[i] // exp
        output[count[index % 10] - 1] = arr[i]
        count[index % 10] -= 1
        i -= 1
    for i in range(n):
        arr[i] = output[i]

# 48. Exchange two numbers without a third variable
def swap_numbers(a, b):
    a = a + b
    b = a - b
    a = a - b
    return a, b

# 49. Check if two rectangles overlap
def rectangles_overlap(rect1, rect2):
    return (rect1[0] < rect2[2] and rect1[2] > rect2[0] and
            rect1[1] < rect2[3] and rect1[3] > rect2[1])

# 50. Vending machine design (basic structure)
class VendingMachine:
    def __init__(self):
        self.items = {}
        self.balance = 0

    def add_item(self, name, price, quantity):
        self.items[name] = {'price': price, 'quantity': quantity}

    def insert_money(self, amount):
        self.balance += amount

    def select_item(self, name):
        if name not in self.items:
            return "Item not available"
        if self.items[name]['quantity'] == 0:
            return "Item out of stock"
        if self.balance < self.items[name]['price']:
            return "Insufficient balance"
        self.balance -= self.items[name]['price']
        self.items[name]['quantity'] -= 1
        return f"Dispensing {name}"

    def return_change(self):
        change = self.balance
        self.balance = 0
        return change












