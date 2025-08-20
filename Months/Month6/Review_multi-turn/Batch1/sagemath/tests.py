import unittest
from unittest.mock import MagicMock
import sys

# Define a mock Element class to support arithmetic operations in GF(q)
class MockElement:
    def __init__(self, value, modulus=5):
        self.value = value % modulus
        self.modulus = modulus
    
    def __neg__(self):
        return MockElement(-self.value, self.modulus)
    
    def __eq__(self, other):
        return isinstance(other, MockElement) and self.value == other.value
    
    def __mul__(self, other):
        if isinstance(other, int):
            return MockElement(self.value * other, self.modulus)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __repr__(self):
        return str(self.value)

class MockPolynomialRing:
    def __init__(self, field):
        self.field = field
    
    def quotient(self, poly):
        return self

    def __call__(self, value):
        return MockElement(value, self.field)

class MockMatrix:
    def __init__(self, modulus, n, m):
        self.data = [[MockElement(0, modulus) for _ in range(m)] for _ in range(n)]
    
    def __getitem__(self, index):
        i, j = index
        return self.data[i][j]
    
    def __setitem__(self, index, value):
        i, j = index
        self.data[i][j] = value
    
    def __len__(self):
        return len(self.data)
    
    def __repr__(self):
        return "\n".join([" ".join([str(elem) for elem in row]) for row in self.data])

# Mock sage.all with the finite field and polynomial ring
mock_sage_all = MagicMock()
mock_sage_all.GF = lambda q: q  # Mock finite field GF(q) as just the modulus value
mock_sage_all.PolynomialRing = lambda F: MockPolynomialRing(F)
mock_sage_all.Matrix = MockMatrix
sys.modules["sage.all"] = mock_sage_all

from ideal_completion import rot

class TestRotFunction(unittest.TestCase):

    def setUp(self):
        # Set up the finite fields and polynomial rings
        self.F5 = mock_sage_all.GF(5)
        self.F7 = mock_sage_all.GF(7)
        self.R5 = mock_sage_all.PolynomialRing(self.F5)
        self.R7 = mock_sage_all.PolynomialRing(self.F7)
        self.S5 = self.R5.quotient("x^2 + 1")
        self.S7 = self.R7.quotient("x^3 + x + 1")

    def test_rot_zero_vector(self):
        # This test checks the rot function’s behavior with a zero vector.
        # It ensures that the resulting matrix is also filled with zeros, which is a critical edge case to verify the function's correctness.

        s = [self.S5(0), self.S5(0), self.S5(0)]
        self.mock_vector = MagicMock()
        self.mock_vector.__len__.return_value = len(s)
        self.mock_vector.__getitem__.side_effect = lambda i: s[i]
        self.mock_vector.base_ring.return_value = self.F5

        expected_matrix = [
            [MockElement(0, 5), MockElement(0, 5), MockElement(0, 5)],
            [MockElement(0, 5), MockElement(0, 5), MockElement(0, 5)],
            [MockElement(0, 5), MockElement(0, 5), MockElement(0, 5)]
        ]

        M = rot(self.mock_vector)
        for i in range(len(expected_matrix)):
            for j in range(len(expected_matrix)):
                self.assertEqual(M[i, j], expected_matrix[i][j])

    def test_rot_single_element_vector(self):
        # This test evaluates the rot function when given a single-element vector.
        # It is essential to confirm that the function can handle the simplest case correctly and produce a 1x1 matrix with the same element.

        s = [self.S5(1)]
        self.mock_vector = MagicMock()
        self.mock_vector.__len__.return_value = len(s)
        self.mock_vector.__getitem__.side_effect = lambda i: s[i]
        self.mock_vector.base_ring.return_value = self.F5

        expected_matrix = [[MockElement(1, 5)]]

        M = rot(self.mock_vector)
        self.assertEqual(M[0, 0], expected_matrix[0][0])

    def test_rot_different_field(self):
        # this test checks the rot function with a vector from a different field (F_7) to ensure that the function can handle different fields correctly.
        # This is important to verify that the function is not dependent on a specific field and can work with any finite field.

        s = [self.S7(1), self.S7(3), self.S7(5)]
        self.mock_vector = MagicMock()
        self.mock_vector.__len__.return_value = len(s)
        self.mock_vector.__getitem__.side_effect = lambda i: s[i]
        self.mock_vector.base_ring.return_value = self.F7

        expected_matrix = [
            [MockElement(1, 7), MockElement(2, 7), MockElement(4, 7)],
            [MockElement(3, 7), MockElement(1, 7), MockElement(2, 7)],
            [MockElement(5, 7), MockElement(3, 7), MockElement(1, 7)]
        ]

        M = rot(self.mock_vector)
       
        for i in range(len(expected_matrix)):
            for j in range(len(expected_matrix)):
                self.assertEqual(M[i, j], expected_matrix[i][j])

    def test_rot_larger_vector(self):
        # This test checks the rot function with a larger vector to confirm correct matrix formation and rotational logic.
        # This is important to ensure the function scales well and handles increased vector sizes without errors.

        s = [self.S5(1), self.S5(2), self.S5(3), self.S5(4)]
        self.mock_vector = MagicMock()
        self.mock_vector.__len__.return_value = len(s)
        self.mock_vector.__getitem__.side_effect = lambda i: s[i]
        self.mock_vector.base_ring.return_value = self.F5

        expected_matrix = [
            [MockElement(1, 5), MockElement(1, 5), MockElement(2, 5), MockElement(3, 5)],
            [MockElement(2, 5), MockElement(1, 5), MockElement(1, 5), MockElement(2, 5)],
            [MockElement(3, 5), MockElement(2, 5), MockElement(1, 5), MockElement(1, 5)],
            [MockElement(4, 5), MockElement(3, 5), MockElement(2, 5), MockElement(1, 5)]
        ]

        M = rot(self.mock_vector)
        for i in range(len(expected_matrix)):
            for j in range(len(expected_matrix)):
                self.assertEqual(M[i, j], expected_matrix[i][j])

    def test_rot_F5_x2_plus_1(self):
        # This test specifically evaluates the rot function with F_5 and f(x) = x^2 + 1.
        # It verifies the correct application of rotational logic in the finite field F_5 with the given polynomial f(x).
       
        # Vector in the quotient ring F_5[x] / (x^2 + 1)
        s = [self.S5(1), self.S5(2), self.S5(3)]

        # Mock the vector behavior
        self.mock_vector = MagicMock()
        self.mock_vector.__len__.return_value = len(s)
        self.mock_vector.__getitem__.side_effect = lambda i: s[i]
        self.mock_vector.base_ring.return_value = self.F5

        # Expected matrix for the given vector
        expected_matrix = [
            [MockElement(1, 5), MockElement(2, 5), MockElement(3, 5)],
            [MockElement(2, 5), MockElement(1, 5), MockElement(2, 5)],
            [MockElement(3, 5), MockElement(2, 5), MockElement(1, 5)]
        ]

        # Calculate the rotation matrix using rot
        M = rot(self.mock_vector)

        # Compare each element in the resulting matrix to the expected values
        for i in range(len(expected_matrix)):
            for j in range(len(expected_matrix)):
                self.assertEqual(M[i, j], expected_matrix[i][j])

if __name__ == '__main__':
    unittest.main(verbosity=2)