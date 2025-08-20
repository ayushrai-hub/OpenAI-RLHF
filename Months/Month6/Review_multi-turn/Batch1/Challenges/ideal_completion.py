def cleave(A1, A2, j):
    if not ((isinstance(A1, str) and isinstance(A2, str)) or (isinstance(A1, tuple) and isinstance(A2, tuple))):
        raise TypeError("Both A1 and A2 must be of the same type, either both strings or both tuples.")
    if not (isinstance(j, int) and j >= 0):
        raise ValueError("j must be a non-negative integer.")
    new_A1 = A1[:j] + A2[j:]
    new_A2 = A2[:j] + A1[j:]
    return new_A1, new_A2
