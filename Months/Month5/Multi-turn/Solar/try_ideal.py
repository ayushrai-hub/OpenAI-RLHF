import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def generate_solar_output() -> pd.DataFrame:
    """
    Generate hourly solar production data for a full year (8760 hours), 
    accounting for daily and seasonal variations.
    Returns:
        pd.DataFrame: DataFrame with 'timestamp' and 'solar_power' columns.
    """
    # Define parameters for simulation
    hours_per_year = 8760
    days_per_year = 365
    peak_solar_output = 1.0  # 1 MW max output
    
    # Generate seasonal variation using a sine wave (scaled between 0 and 1)
    day_of_year = np.arange(hours_per_year) / 24
    seasonal_variation = 0.8 + 0.2 * np.sin(2 * np.pi * day_of_year / days_per_year)
    
    # Generate daily variation with another sine wave
    hours_in_day = np.arange(24)
    daily_variation = np.sin(np.pi * hours_in_day / 24)  # Solar production peaks at noon
    
    # Repeat daily variation for each day of the year
    daily_variation_full = np.tile(daily_variation, days_per_year)
    
    # Combine daily and seasonal variations
    solar_output = peak_solar_output * daily_variation_full * seasonal_variation
    
    # Add some randomness to simulate real-world fluctuations (e.g., weather, clouds)
    solar_output += np.random.normal(0, 0.05, hours_per_year)  # Add small random noise
    solar_output = np.clip(solar_output, 0, peak_solar_output)  # Ensure values are in [0, 1]
    
    # Create a DataFrame
    df = pd.DataFrame({
        "timestamp": pd.date_range(start="2023-01-01", end="2023-12-31 23:00", freq="h"),  # Use 'h' for hourly
        "solar_power": solar_output
    })
    return df


def simulate_battery(df: pd.DataFrame, battery_capacity: float) -> tuple[np.ndarray, np.ndarray, float]:
    """
    Simulates the operation of a battery system with a given capacity.
    
    Args:
        df (pd.DataFrame): DataFrame with a 'solar_power' column (in MW).
        battery_capacity (float): Battery capacity in MWh.
    
    Returns:
        tuple[np.ndarray, np.ndarray, float]: Battery state of charge, total output, and unmet load share.
    """
    hours_per_year = 8760
    load = 1.0  # 1 MW constant load
    battery_state_of_charge = np.zeros(hours_per_year)  # State of charge in MWh
    battery_efficiency = 0.85  # 85% round-trip efficiency
    battery_state_of_charge[0] = 0.5 * battery_capacity  # Initial charge at 50%
    solar_output = df["solar_power"].values
    total_output = np.zeros(hours_per_year)
    unmet_load = 0.0

    for t in range(hours_per_year):
        # Calculate excess solar power after serving the load
        excess_solar = solar_output[t] - load if solar_output[t] > load else 0
        
        # Charge the battery with excess solar
        if excess_solar > 0:
            charge_amount = min(excess_solar * battery_efficiency, 
                                battery_capacity - battery_state_of_charge[t])
            battery_state_of_charge[t] += charge_amount / battery_efficiency
        
        # Discharge the battery to meet the load deficit
        load_deficit = load - solar_output[t] if solar_output[t] < load else 0
        if load_deficit > 0:
            discharge_amount = min(load_deficit, battery_state_of_charge[t])
            battery_state_of_charge[t] -= discharge_amount
            total_output[t] = solar_output[t] + discharge_amount
        else:
            total_output[t] = solar_output[t]
        
        # Track unmet load
        if total_output[t] < load:
            unmet_load += load - total_output[t]
        
        # Ensure battery state is updated for the next hour
        if t < hours_per_year - 1:
            battery_state_of_charge[t + 1] = battery_state_of_charge[t]

    # Calculate unmet load share (normalized to be between 0 and 1)
    unmet_load_share = unmet_load / (load * hours_per_year)

    return battery_state_of_charge, total_output, unmet_load_share


def main() -> None:
    """
    Main function to simulate the solar farm and battery system, and generate visualizations.
    """
    # Generate solar output data
    solar_data = generate_solar_output()
    
    # Define parameters for battery simulation
    battery_capacities = np.linspace(0, 168, 20)  # Battery capacities from 0 to 168 MWh
    unmet_load_shares = []

    # Run simulations for different battery capacities
    for capacity in battery_capacities:
        _, _, unmet_load_share = simulate_battery(solar_data, capacity)
        unmet_load_shares.append(unmet_load_share)

    # Visualize solar output, battery state of charge, and total output
    battery_capacity = 50  # Example battery capacity in MWh
    soc, total_output, unmet_load_share = simulate_battery(solar_data, battery_capacity)

    # Plot solar generation and battery state of charge
    plt.figure(figsize=(15, 8))

    # Solar generation plot
    plt.subplot(3, 1, 1)
    plt.plot(solar_data["timestamp"], solar_data["solar_power"], label="Solar Power (MW)", color="gold")
    plt.title("Solar Farm Simulation (1 MW DC)")
    plt.ylabel("Solar Power (MW)")
    plt.legend()
    
    # Battery state of charge plot
    plt.subplot(3, 1, 2)
    plt.plot(solar_data["timestamp"], soc, label="Battery State of Charge (MWh)", color="blue")
    plt.ylabel("Battery SOC (MWh)")
    plt.legend()
    
    # Combined output plot
    plt.subplot(3, 1, 3)
    plt.plot(solar_data["timestamp"], total_output, label="Total Output (MW)", color="green")
    plt.axhline(1.0, color="red", linestyle="--", label="Load (1 MW)")
    plt.ylabel("Total Output (MW)")
    plt.legend()

    plt.xlabel("Time")
    plt.tight_layout()
    plt.show()

    # Plot relationship between battery capacity and unmet load share
    plt.figure(figsize=(10, 6))
    plt.plot(battery_capacities, unmet_load_shares, marker="o", color="purple")
    plt.title("Battery Capacity vs. Unmet Load Share")
    plt.xlabel("Battery Capacity (MWh)")
    plt.ylabel("Unmet Load Share (fraction)")
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()