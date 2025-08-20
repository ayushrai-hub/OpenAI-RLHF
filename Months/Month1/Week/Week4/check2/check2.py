def simulate_water_transfer(rows, cols, street_network_grid, river_network_grid, elev_GRID, elev_GRID_normalized, water_level, diffusion_fraction, alpha, zzz):
    new_water_level = water_level.copy()

    for i in range(rows):
        for j in range(cols):
            if not (street_network_grid[i, j] == 1 or river_network_grid[i, j] == 1):
                continue
            
            neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
            valid_neighbors = [(ni, nj) for ni, nj in neighbors if 0 <= ni < rows and 0 <= nj < cols]

            for ni, nj in valid_neighbors:
                if not (street_network_grid[ni, nj] == 1 or river_network_grid[ni, nj] == 1):
                    continue

                if elev_GRID[ni, nj] < elev_GRID[i, j] or (elev_GRID[ni, nj] > elev_GRID[i, j] and river_network_grid[i, j] == 1 and water_level[i, j] > 2 + elev_GRID_normalized[i, j]):
                    elevation_difference = abs(elev_GRID_normalized[i, j] - elev_GRID_normalized[ni, nj])
                    transfer_amount = min(diffusion_fraction * water_level[i, j], water_level[i, j] * np.exp(-alpha * elevation_difference))
                    transfer_amount = min(transfer_amount, water_level[i, j])

                    if new_water_level[i, j] - transfer_amount < 0:
                        transfer_amount = new_water_level[i, j]

                    if elev_GRID[ni, nj] < elev_GRID[i, j]:
                        if river_network_grid[i, j] == 1:
                            new_water_level[i, j] += transfer_amount * ((zzz / 5) ** 0.1) - 0.2
                        new_water_level[i, j] -= transfer_amount
                        new_water_level[ni, nj] += transfer_amount
                        new_water_level[i, j] += new_water_level[i, j] / 32
                        new_water_level[ni, nj] += new_water_level[i, j] * 0.05
                    else:
                        if river_network_grid[i, j] == 1:
                            new_water_level[i, j] += transfer_amount * ((zzz / 5) ** 0.1) - 0.2
                            new_water_level[ni, nj] += transfer_amount / 32
                        else:
                            new_water_level[i, j] -= transfer_amount
                            new_water_level[ni, nj] += transfer_amount
                            new_water_level[i, j] += new_water_level[i, j] / 32
                            new_water_level[ni, nj] += new_water_level[i, j] * 0.05

    return new_water_level, max_velocity
