import unittest
from testableIC import calculate_positions

class TestFibonacciPositions(unittest.TestCase):
    def setUp(self):
        self.positions = calculate_positions()

    def test_no_overlap(self):
        # Test no square overlaps.
        for i in range(len(self.positions)):
            x1, y1, size1 = self.positions[i]
            for j in range(i + 1, len(self.positions)):
                x2, y2, size2 = self.positions[j]
                if not (x1 + size1 <= x2 or x2 + size2 <= x1 or y1 + size1 <= y2 or y2 + size2 <= y1):
                    self.fail()

    def test_spacing(self):
        # Test no space between consecutive squares.
        for i in range(1, len(self.positions)):
            x1, y1, size1 = self.positions[i - 1]
            x2, y2, size2 = self.positions[i]
            if not (x1 + size1 == x2 or y1 - size2 == y2):
                self.fail()

    def test_fibonacci_sequence(self):
        # Test that the sizes of the squares follow the Fibonacci sequence.
        a, b = 0, 1
        for x, y, size in self.positions:
            c = a + b
            self.assertEqual(c, size)
            a = b
            b = c

if __name__ == '__main__':
    unittest.main(verbosity=2)
