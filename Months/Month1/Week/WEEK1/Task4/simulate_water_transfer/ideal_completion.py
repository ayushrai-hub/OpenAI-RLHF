import numpy as np

def simulate_water_transfer(rows, cols, street_network_grid, river_network_grid, elev_GRID, elev_GRID_normalized, water_level, diffusion_fraction, alpha, zzz):
    new_water_level = water_level.copy()
    max_velocity = 0

    for i in range(rows):
        for j in range(cols):
            # Skip cells that are not part of street or river network
            if not (street_network_grid[i, j] or river_network_grid[i, j]):
                continue
            
            neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
            valid_neighbors = [(ni, nj) for ni, nj in neighbors if 0 <= ni < rows and 0 <= nj < cols]

            for ni, nj in valid_neighbors:
                # Skip neighbors that are not part of street or river network
                if not (street_network_grid[ni, nj] or river_network_grid[ni, nj]):
                    continue

                # Calculate elevation difference
                elevation_difference = elev_GRID_normalized[i, j] - elev_GRID_normalized[ni, nj]

                # Determine if transfer should occur based on elevation and water level
                transfer_condition = (elevation_difference > 0) or (river_network_grid[i, j] and water_level[i, j] > 2 + elev_GRID_normalized[i, j])

                if transfer_condition:
                    # Calculate transfer amount
                    transfer_amount = min(
                        diffusion_fraction * water_level[i, j],
                        water_level[i, j] * np.exp(-alpha * abs(elevation_difference)),
                        water_level[i, j],
                        new_water_level[i, j]
                    )

                    # Update water levels
                    new_water_level[i, j] -= transfer_amount
                    new_water_level[ni, nj] += transfer_amount

                    # Additional calculations for river network
                    if river_network_grid[i, j]:
                        river_factor = ((zzz / 5) ** 0.1) - 0.2
                        new_water_level[i, j] += transfer_amount * river_factor

                    # Additional calculations for street network
                    if street_network_grid[i, j]:
                        new_water_level[i, j] += new_water_level[i, j] / 32
                        new_water_level[ni, nj] += new_water_level[i, j] * 0.05

                    # Update max velocity (simplified calculation)
                    current_velocity = transfer_amount / (elevation_difference + 1e-6)
                    max_velocity = max(max_velocity, current_velocity)

    return new_water_level, max_velocity

# Example usage
rows, cols = 10, 10
street_network_grid = np.random.randint(0, 2, (rows, cols))
river_network_grid = np.random.randint(0, 2, (rows, cols))
elev_GRID = np.random.rand(rows, cols) * 100
elev_GRID_normalized = (elev_GRID - elev_GRID.min()) / (elev_GRID.max() - elev_GRID.min())
water_level = np.random.rand(rows, cols) * 10
diffusion_fraction = 0.1
alpha = 0.5
zzz = 25

new_water_level, max_velocity = simulate_water_transfer(
    rows, cols, street_network_grid, river_network_grid, elev_GRID, 
    elev_GRID_normalized, water_level, diffusion_fraction, alpha, zzz
)

print(f"Max velocity: {max_velocity}")
print("New water levels:")
print(new_water_level)

