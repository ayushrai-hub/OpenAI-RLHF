import numpy as np
from original11 import decomposition_model

def test_small_problem():
    values = [1, 2, 3]
    cluster_size = [2, 1]
    Q = np.array([
        [2, 1, 0, 1, 0, 0],
        [1, 2, 1, 0, 1, 0],
        [0, 1, 2, 0, 0, 1],
        [1, 0, 0, 2, 1, 0],
        [0, 1, 0, 1, 2, 1],
        [0, 0, 1, 0, 1, 2]
    ])
    p = np.array([-1, -2, -3, -1, -2, -3])
    r = 0

    best_sol, best_obj = decomposition_model(values, cluster_size, Q, p, r)
    
    expected_sol = np.array([1, 0, 0, 1, 1, 0])
    expected_obj = -4.5

    assert np.allclose(best_sol, expected_sol, atol=1e-6), f"Expected {expected_sol}, but got {best_sol}"
    assert np.isclose(best_obj, expected_obj, atol=1e-6), f"Expected objective {expected_obj}, but got {best_obj}"
    print("Small problem test passed!")

def test_medium_problem():
    values = [1, 2, 3, 4, 5]
    cluster_size = [2, 3]
    n_vars = len(values) * len(cluster_size)
    
    np.random.seed(42)  # For reproducibility
    Q = np.random.rand(n_vars, n_vars)
    Q = (Q + Q.T) / 2  # Ensure Q is symmetric
    p = np.random.rand(n_vars)
    r = 0

    best_sol, best_obj = decomposition_model(values, cluster_size, Q, p, r)

    # Check constraints
    A1 = np.kron(np.eye(len(values)), np.ones(len(cluster_size)))
    A2 = np.kron(np.ones(len(values)), np.eye(len(cluster_size)))
    
    assert np.allclose(A1 @ best_sol, 1), "One cluster per value constraint violated"
    assert np.all(A2 @ best_sol >= 1), "Minimum one value per cluster constraint violated"
    assert np.all(np.logical_or(np.isclose(best_sol, 0), np.isclose(best_sol, 1))), "Solution is not binary"
    
    print("Medium problem test passed!")

def test_infeasible_problem():
    values = [1, 2]
    cluster_size = [3]  # Infeasible because we can't assign 2 values to 3 clusters
    Q = np.array([[1, 0], [0, 1]])
    p = np.array([0, 0])
    r = 0

    best_sol, best_obj = decomposition_model(values, cluster_size, Q, p, r)
    
    assert best_sol is None, "Expected None solution for infeasible problem"
    assert best_obj == float('inf'), "Expected infinite objective for infeasible problem"
    print("Infeasible problem test passed!")

def test_large_problem():
    values = list(range(1, 21))  # 20 values
    cluster_size = [5, 5, 5, 5]  # 4 clusters
    n_vars = len(values) * len(cluster_size)
    
    np.random.seed(42)  # For reproducibility
    Q = np.random.rand(n_vars, n_vars)
    Q = (Q + Q.T) / 2  # Ensure Q is symmetric
    p = np.random.rand(n_vars)
    r = 0

    best_sol, best_obj = decomposition_model(values, cluster_size, Q, p, r, max_iter=200)

    # Check constraints
    A1 = np.kron(np.eye(len(values)), np.ones(len(cluster_size)))
    A2 = np.kron(np.ones(len(values)), np.eye(len(cluster_size)))
    
    assert np.allclose(A1 @ best_sol, 1), "One cluster per value constraint violated"
    assert np.all(A2 @ best_sol >= 1), "Minimum one value per cluster constraint violated"
    assert np.all(np.logical_or(np.isclose(best_sol, 0), np.isclose(best_sol, 1))), "Solution is not binary"
    
    print("Large problem test passed!")

if __name__ == "__main__":
    test_small_problem()
    test_medium_problem()
    test_infeasible_problem()
    test_large_problem()
    print("All tests passed successfully!")