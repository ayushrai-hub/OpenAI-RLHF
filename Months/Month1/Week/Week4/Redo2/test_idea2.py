import unittest
import numpy as np
from redo_idea2 import simulate_water_transfer

class TestWaterTransferSimulation(unittest.TestCase):

    def setUp(self):
        self.rows, self.cols = 5, 5
        self.diffusion_fraction = 0.1
        self.alpha = 0.5
        self.zzz = 25

    

    def test_water_movement(self):
        street_network_grid = np.ones((self.rows, self.cols))
        river_network_grid = np.zeros((self.rows, self.cols))
        elev_GRID = np.ones((self.rows, self.cols))
        elev_GRID[0, 0] = 2
        elev_GRID_normalized = (elev_GRID - elev_GRID.min()) / (elev_GRID.max() - elev_GRID.min())
        water_level = np.zeros((self.rows, self.cols))
        water_level[0, 0] = 10

        new_water_level, _ = simulate_water_transfer(
            self.rows, self.cols, street_network_grid, river_network_grid, 
            elev_GRID, elev_GRID_normalized, water_level, 
            self.diffusion_fraction, self.alpha, self.zzz
        )

        self.assertLess(new_water_level[0, 0], water_level[0, 0],
                        "Water should move from higher to lower elevation")

    def test_max_velocity(self):
        street_network_grid = np.ones((self.rows, self.cols))
        river_network_grid = np.zeros((self.rows, self.cols))
        elev_GRID = np.ones((self.rows, self.cols))
        elev_GRID[0, 0] = 2
        elev_GRID_normalized = (elev_GRID - elev_GRID.min()) / (elev_GRID.max() - elev_GRID.min())
        water_level = np.zeros((self.rows, self.cols))
        water_level[0, 0] = 10

        _, max_velocity = simulate_water_transfer(
            self.rows, self.cols, street_network_grid, river_network_grid, 
            elev_GRID, elev_GRID_normalized, water_level, 
            self.diffusion_fraction, self.alpha, self.zzz
        )

        self.assertGreater(max_velocity, 0, "Max velocity should be positive")

    def test_no_negative_water_levels(self):
        street_network_grid = np.random.randint(0, 2, (self.rows, self.cols))
        river_network_grid = np.random.randint(0, 2, (self.rows, self.cols))
        elev_GRID = np.random.rand(self.rows, self.cols) * 100
        elev_GRID_normalized = (elev_GRID - elev_GRID.min()) / (elev_GRID.max() - elev_GRID.min())
        water_level = np.random.rand(self.rows, self.cols) * 10

        new_water_level, _ = simulate_water_transfer(
            self.rows, self.cols, street_network_grid, river_network_grid, 
            elev_GRID, elev_GRID_normalized, water_level, 
            self.diffusion_fraction, self.alpha, self.zzz
        )

        self.assertTrue(np.all(new_water_level >= 0), "Water levels should never be negative")

if __name__ == '__main__':
    unittest.main(verbosity=2)