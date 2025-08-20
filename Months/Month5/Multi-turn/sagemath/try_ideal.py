import sys
from unittest.mock import MagicMock
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


def rot(s):
    """
    Constructs an n x n rotation matrix from a vector s in a quotient ring F_q[x]/(f(x)).
    
    Args:
        s: A vector in F_q[x]/(f(x)) representing the coefficients
        
    Returns:
        An n x n matrix where elements are derived from s using modular indexing
    """
    n = len(s)
    F = s.base_ring()
    
    # Initialize the matrix with the appropriate dimensions and field
    M = Matrix(F, n, n)
    
    # Fill the matrix according to the rotation pattern
    for i in range(n):
        for j in range(n):
            # Calculate the index with modular arithmetic
            idx = (j - i) % n
            
            # Set the matrix element
            # For first row: s0, -s(n-1), -s(n-2), ..., -s1
            # For subsequent rows: shift the pattern right
            if i == 0 and j > 0:
                M[i, j] = -s[n - j]
            else:
                M[i, j] = s[idx]
    
    return M