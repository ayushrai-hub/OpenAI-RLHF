#ideal_completion.py
import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt

# Configuration
dimension = 3  # Size of the square matrix
np.random.seed(0)  # Seed for reproducibility

def create_matrix_with_condition_number(dimension: int, cond_num: float) -> np.ndarray:
    """Create a matrix with specified condition number."""
    try:
        random_matrix_A = np.random.rand(dimension, dimension) + 1j * np.random.rand(dimension, dimension)
        random_matrix_B = np.random.rand(dimension, dimension) + 1j * np.random.rand(dimension, dimension)
        
        # QR decomposition to obtain unitary matrices
        unitary_Q1, _ = np.linalg.qr(random_matrix_A)
        unitary_Q2, _ = np.linalg.qr(random_matrix_B)
        
        # Create singular values
        max_singular_value = 1.0
        min_singular_value = max_singular_value / cond_num
        singular_values_arr = np.linspace(max_singular_value, min_singular_value, dimension)
        singular_values_matrix = np.diag(singular_values_arr)
        
        # Form matrix A with desired condition number
        matrix_A = unitary_Q1 @ singular_values_matrix @ unitary_Q2.conj().T
        return matrix_A
    except Exception as e:
        print(f"Error creating matrix with condition number {cond_num}: {e}")
        return None  # Return None to indicate failure

def main():
    # List of various condition numbers to check
    condition_numbers_list = [1e1, 1e2, 1e3, 1e4, 1e5]

    # Trace distance threshold setting
    trace_distance_limit = 0.1

    # Arrays for storing results
    time_needed_array = []
    condition_number_array = []

    for cond_num in condition_numbers_list:
        print(f"Analyzing condition number: {cond_num}")
        
        # Attempt to create A with the specified condition number
        matrix_A = create_matrix_with_condition_number(dimension, cond_num)
        
        if matrix_A is None:
            print(f"Skipping condition number {cond_num} due to matrix creation failure.")
            continue  # Skip to the next condition number if creation failed
        
        # Generate and normalize vector b
        vector_b = np.random.rand(dimension) + 1j * np.random.rand(dimension)
        normalized_b = vector_b / np.linalg.norm(vector_b)
        
        # Solve for x in Ax = b
        try:
            solution_x = np.linalg.solve(matrix_A, normalized_b)
        except la.LinAlgError as e:
            print(f"Matrix with condition number {cond_num} is singular or nearly singular: {e}")
            continue  # Skip this condition number and proceed to the next one
        
        # Calculate target density matrix rho_target = x x† / ||x||²
        magnitude_squared_x = np.vdot(solution_x, solution_x)
        density_matrix_target = np.outer(solution_x, np.conj(solution_x)) / magnitude_squared_x
        
        # Initialize rho(0) = b b†
        density_matrix_rho = np.outer(normalized_b, np.conj(normalized_b))
        
        # Define Q_b = I - b b†
        transformation_Q_b = np.eye(dimension) - np.outer(normalized_b, np.conj(normalized_b))
        
        # Define V = Q_b A
        matrix_V = transformation_Q_b @ matrix_A
        
        # Time configurations
        time_step = 0.01  # Time increment
        maximum_time = 1000  # Max time
        maximum_iterations = int(maximum_time / time_step)
        
        # Arrays for trace distances and time tracking
        track_trace_distances = []
        record_times = []
        
        time_necessary = None  # Initialize necessary time variable
        for iteration in range(maximum_iterations):
            current_time = iteration * time_step
            # Compute drho/dt using Lindblad equation formulation
            VrhoVdag = matrix_V @ density_matrix_rho @ matrix_V.conj().T
            VdagV = matrix_V.conj().T @ matrix_V
            differential_rho = VrhoVdag - 0.5 * (VdagV @ density_matrix_rho + density_matrix_rho @ VdagV)
            
            # Update rho with computed differential
            density_matrix_rho += time_step * differential_rho
            
            # Ensure rho remains Hermitian
            density_matrix_rho = (density_matrix_rho + density_matrix_rho.conj().T) / 2
            
            # Calculate and track trace distances
            delta_rho = density_matrix_rho - density_matrix_target
            eigen_vals = la.eigvalsh(delta_rho)
            trace_distance = 0.5 * np.sum(np.abs(eigen_vals))
            
            # Log trace distance and time
            track_trace_distances.append(trace_distance)
            record_times.append(current_time)
            
            # Evaluate if trace distance is below the threshold
            if trace_distance <= trace_distance_limit:
                time_necessary = current_time
                print(f"Condition number {cond_num}: Trace distance under threshold at time {time_necessary}")
                break  # Exit the time evaluation loop

        if time_necessary is None:
            print(f"Condition number {cond_num}: Threshold not met within t_max = {maximum_time}")
            time_necessary = maximum_time  # Use max time for plotting if threshold isn't met

        # Store necessary values
        time_needed_array.append(time_necessary)
        condition_number_array.append(cond_num)

    # Plot results with error handling
    try:
        plt.figure(figsize=(8, 6))
        plt.plot(condition_number_array, time_needed_array, 'o-', label='Convergence Time', markersize=8)

        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('Condition Number of A (log scale)', fontsize=12)
        plt.ylabel('Time to Reach Trace Distance Threshold (log scale)', fontsize=12)
        plt.title(f'Convergence Time vs Condition Number of A\n(Trace Distance Threshold = {trace_distance_limit})', fontsize=14)

        # Customizing y-axis ticks and minor gridlines for better readability
        plt.ylim(1, max(time_needed_array) * 1.5)  # Adjust the limit based on max time
        plt.yticks([1, 10, 100, 1000, 10000], labels=['$10^0$', '$10^1$', '$10^2$', '$10^3$', '$10^4$'])
        plt.grid(True, which='both', linestyle='--', linewidth=0.7)
        plt.minorticks_on()
        plt.grid(which='minor', linestyle=':', linewidth=0.5)
        plt.legend()
        plt.show()
    except Exception as e:
        print(f"Error during plotting: {e}")

if __name__ == "__main__":
    main()
