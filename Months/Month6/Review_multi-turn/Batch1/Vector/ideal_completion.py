import numpy as np
import matplotlib.pyplot as plt

def create_matrix_with_condition_number(dimension: int, cond_num: float) -> np.ndarray:
    if dimension <= 0 or not isinstance(dimension, int) or cond_num <= 0:
        return None
    np.random.seed(0)
    U, _ = np.linalg.qr(np.random.randn(dimension, dimension))
    V, _ = np.linalg.qr(np.random.randn(dimension, dimension))
    singular_values = np.linspace(cond_num, 1, dimension)
    S = np.diag(singular_values)
    return U @ S @ V.T

def main() -> None:
    np.random.seed(0)
    dimensions = 5
    condition_numbers = [1, 10, 100, 1000, 10000]
    threshold = 0.1
    times_to_threshold = []

    for cond_num in condition_numbers:
        A = create_matrix_with_condition_number(dimensions, cond_num)
        if A is None:
            continue
        b = np.random.randn(dimensions, 1)
        b = b / np.linalg.norm(b)

        x = np.linalg.solve(A, b)
        x = x / np.linalg.norm(x)

        Q_b = np.eye(dimensions) - b @ b.conj().T
        V = Q_b @ A

        V_dag_V = V.conj().T @ V
        norm_factor = np.linalg.norm(V_dag_V)

        def lindblad_rhs(rho):
            return (V @ rho @ V.conj().T - 0.5 * (V_dag_V @ rho + rho @ V_dag_V)) / (norm_factor + 1e-10)

        rho = b @ b.conj().T

        dt = 0.001  # Smaller time step to prevent overflow
        max_steps = 100000  # Increased steps due to smaller dt
        time = 0

        for step in range(max_steps):
            drho_dt = lindblad_rhs(rho)
            rho += drho_dt * dt
            rho = (rho + rho.conj().T) / 2  # Ensuring hermiticity

            # Ensuring rho remains positive semidefinite
            eigvals, eigvecs = np.linalg.eigh(rho)
            eigvals = np.maximum(eigvals, 0)
            rho = eigvecs @ np.diag(eigvals) @ eigvecs.conj().T

            # Renormalizing rho to maintain trace condition
            rho /= (np.trace(rho) + 1e-10)

            target_rho = x @ x.conj().T
            trace_distance = 0.5 * np.trace(np.abs(rho - target_rho))

            if trace_distance < threshold:
                times_to_threshold.append(time)
                break

            time += dt
        else:
            times_to_threshold.append(time)

    plt.plot(condition_numbers, times_to_threshold, marker='o')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Condition Number of A')
    plt.ylabel(f'Time to Reach Trace Distance < {threshold}')
    plt.title('Convergence Time vs. Condition Number')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
