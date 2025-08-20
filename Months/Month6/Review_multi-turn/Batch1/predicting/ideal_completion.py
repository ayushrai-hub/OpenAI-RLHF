import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Starting composition of forces
initial_assets = {
    'Fighter Jets': 50,
    'Drones': 100,
    'Reconnaissance Satellites': 5,
    'Naval Ships': 10
}

# Known daily loss rates (mean and standard deviation)
loss_rates = {
    'Fighter Jets': {'mean': 0.02, 'std': 0.006},
    'Drones': {'mean': 0.035, 'std': 0.01},
    'Reconnaissance Satellites': {'mean': 0.005, 'std': 0.002},
    'Naval Ships': {'mean': 0.007, 'std': 0.003}
}

def simulate_operation(simulation_runs: int, operation_length: int) -> pd.DataFrame:
    # Prepare an array to store the simulation results
    results = {unit: np.zeros((simulation_runs, operation_length + 1)) for unit in initial_assets}
    
    # Initialize with starting numbers
    for unit, count in initial_assets.items():
        results[unit][:, 0] = count
    
    # Run simulations
    for i in range(simulation_runs):
        for day in range(1, operation_length + 1):
            for unit in initial_assets:
                current_count = results[unit][i, day - 1]
                loss_rate = np.random.normal(loss_rates[unit]['mean'], loss_rates[unit]['std'])
                loss_rate = max(0, min(loss_rate, 1))  # Ensure loss rate is between 0 and 1
                losses = np.random.binomial(n=int(current_count), p=loss_rate)
                results[unit][i, day] = current_count - losses

    # Extract only the final day results
    data = []
    final_day = operation_length
    for i in range(simulation_runs):
        row = {'Simulation': i, 'Day': final_day}
        for unit in initial_assets:
            row[unit] = results[unit][i, final_day]
        data.append(row)
    
    df = pd.DataFrame(data)
    return df

def drop_below_threshold_probabilities(results: pd.DataFrame, thresholds: dict, simulation_runs: int) -> dict:
    probabilities = {}
    for unit, threshold in thresholds.items():
        below_threshold = results[unit] < threshold
        probabilities[unit] = below_threshold.sum() / simulation_runs
    return probabilities

def confidence_intervals(results: pd.DataFrame) -> dict:
    intervals = {}
    for unit in initial_assets:
        unit_results = results[unit]
        mean = unit_results.mean()
        std = unit_results.std()
        ci_lower = mean - 1.96 * std
        ci_upper = mean + 1.96 * std
        intervals[unit] = (max(0, ci_lower), ci_upper)  # Lower bound can't be negative
    return intervals

def sensitivity_analysis_on_drones(simulation_runs: int, operation_length: int) -> tuple:
    mu_values = np.linspace(0.01, 0.06, 10)  # Vary mean loss rate from 1% to 6% in 10 steps
    drone_means = []

    for mu in mu_values:
        # Update the mean loss rate for drones
        original_mu = loss_rates['Drones']['mean']
        loss_rates['Drones']['mean'] = mu
        # Simulate
        results = simulate_operation(simulation_runs, operation_length)
        drone_mean = results['Drones'].mean()
        drone_means.append(drone_mean)
        # Reset the mean loss rate
        loss_rates['Drones']['mean'] = original_mu

    # Plotting the sensitivity analysis
    plt.figure(figsize=(10, 6))
    plt.plot(mu_values, drone_means, marker='o')
    plt.title('Sensitivity Analysis of Drone Loss Rate')
    plt.xlabel('Mean Daily Loss Rate')
    plt.ylabel('Average Number of Drones on Final Day')
    plt.grid(True)
    plt.savefig('sensitivity_analysis.png')
    plt.close()

    return mu_values, drone_means

def probability_of_retaining_80_percent(results: pd.DataFrame, initial_assets: dict, simulation_runs: int) -> float:
    criteria = np.ones(simulation_runs, dtype=bool)
    for unit, initial_count in initial_assets.items():
        final_counts = results[unit].values
        required_count = 0.8 * initial_count
        criteria &= (final_counts >= required_count)
    return float(criteria.sum() / simulation_runs)
