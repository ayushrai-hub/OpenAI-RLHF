import numpy as np

def rot(vector):
    n = len(vector)
    M = np.empty((n, n), dtype=object)
    for i in range(n):
        for j in range(n):
            idx = (i - j) % n
            sign = 1 if j == 0 or i - j >= 0 else -1
            M[i, j] = sign * vector[idx]
    return M
