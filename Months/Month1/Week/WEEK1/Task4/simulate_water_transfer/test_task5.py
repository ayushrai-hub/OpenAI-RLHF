import numpy as np
import unittest
from unittest.mock import patch

# Import the function to be tested
from task5_user import simulate_water_transfer

class TestSimulateWaterTransfer(unittest.TestCase):

    def setUp(self):
        # Set up common test data
        self.rows, self.cols = 3, 3
        self.diffusion_fraction = 0.1
        self.alpha = 0.5
        self.zzz = 25

    def test_no_transfer_on_flat_surface(self):
        # Test that no water transfer occurs on a flat surface
        street_network_grid = np.ones((self.rows, self.cols))
        river_network_grid = np.zeros((self.rows, self.cols))
        elev_GRID = np.ones((self.rows, self.cols))
        elev_GRID_normalized = np.ones((self.rows, self.cols))
        water_level = np.ones((self.rows, self.cols))

        new_water_level, max_velocity = simulate_water_transfer(
            self.rows, self.cols, street_network_grid, river_network_grid,
            elev_GRID, elev_GRID_normalized, water_level,
            self.diffusion_fraction, self.alpha, self.zzz
        )

        np.testing.assert_array_almost_equal(new_water_level, water_level)
        self.assertAlmostEqual(max_velocity, 0)

    def test_water_transfer_downhill(self):
        # Test water transfer from higher to lower elevation
        street_network_grid = np.ones((self.rows, self.cols))
        river_network_grid = np.zeros((self.rows, self.cols))
        elev_GRID = np.array([[2, 2, 2], [2, 1, 2], [2, 2, 2]])
        elev_GRID_normalized = (elev_GRID - elev_GRID.min()) / (elev_GRID.max() - elev_GRID.min())
        water_level = np.ones((self.rows, self.cols))

        new_water_level, max_velocity = simulate_water_transfer(
            self.rows, self.cols, street_network_grid, river_network_grid,
            elev_GRID, elev_GRID_normalized, water_level,
            self.diffusion_fraction, self.alpha, self.zzz
        )

        # Check that water level decreased in higher cells and increased in lower cell
        self.assertLess(new_water_level[0, 1], 1)
        self.assertLess(new_water_level[1, 0], 1)
        self.assertLess(new_water_level[1, 2], 1)
        self.assertLess(new_water_level[2, 1], 1)
        self.assertGreater(new_water_level[1, 1], 1)

    def test_max_velocity_calculation(self):
        # Test that max_velocity is calculated correctly
        street_network_grid = np.ones((self.rows, self.cols))
        river_network_grid = np.zeros((self.rows, self.cols))
        elev_GRID = np.array([[2, 2, 2], [2, 0, 2], [2, 2, 2]])
        elev_GRID_normalized = (elev_GRID - elev_GRID.min()) / (elev_GRID.max() - elev_GRID.min())
        water_level = np.ones((self.rows, self.cols)) * 2

        _, max_velocity = simulate_water_transfer(
            self.rows, self.cols, street_network_grid, river_network_grid,
            elev_GRID, elev_GRID_normalized, water_level,
            self.diffusion_fraction, self.alpha, self.zzz
        )

        self.assertGreater(max_velocity, 0)

    @patch('numpy.random.rand')
    def test_random_input(self, mock_rand):
        # Test with random input to ensure no errors occur
        mock_rand.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]])
        
        street_network_grid = np.random.randint(0, 2, (self.rows, self.cols))
        river_network_grid = np.random.randint(0, 2, (self.rows, self.cols))
        elev_GRID = np.random.rand(self.rows, self.cols) * 100
        elev_GRID_normalized = (elev_GRID - elev_GRID.min()) / (elev_GRID.max() - elev_GRID.min())
        water_level = np.random.rand(self.rows, self.cols) * 10

        try:
            new_water_level, max_velocity = simulate_water_transfer(
                self.rows, self.cols, street_network_grid, river_network_grid,
                elev_GRID, elev_GRID_normalized, water_level,
                self.diffusion_fraction, self.alpha, self.zzz
            )
        except Exception as e:
            self.fail(f"simulate_water_transfer raised {type(e).__name__} unexpectedly!")

        self.assertEqual(new_water_level.shape, (self.rows, self.cols))
        self.assertIsInstance(max_velocity, (int, float))

if __name__ == '__main__':
    unittest.main(verbosity=2)