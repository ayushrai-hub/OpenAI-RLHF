import unittest
import numpy as np
import matplotlib.pyplot as plt
from unittest.mock import patch
from ideal_completion import neighbours, wolff_step, simulate_potts

class TestPottsModel(unittest.TestCase):
 
    def test_neighbours(self):
        """Test the neighbours function for correct periodic boundary conditions."""
        L = 5
        x, y = 0, 0  # Define a corner point of the grid for testing neighbors
        expected_neighbours = [(0, 4), (0, 1), (4, 0), (1, 0)]  # Expected neighbors with periodic boundaries
        
        # Assert that the neighbours function returns the expected neighbors
        self.assertEqual(neighbours(L, x, y), expected_neighbours, 
                         "Neighbours function does not return correct neighbors with periodic boundaries.")
        # Importance: Ensures that the function correctly calculates periodic neighbors, 
        # which is critical for the accurate simulation of the Potts model.

    def test_wolff_step(self):
        L=5 # Define a smaller grid for quick testing
        q=3 # Number of Potts states
        beta = 0.5 # Inverse temperature
        grid = np.random.randint(0, q, (L, L))
        """Test the wolff_step function to check if clusters are formed and flipped."""
        initial_grid = grid.copy()  # Store the initial state of the grid
        cluster_size = wolff_step(grid, beta, q)  # Execute a single Wolff step
        
        # Assert that the grid has changed after the Wolff step
        self.assertNotEqual(initial_grid.tolist(), grid.tolist(), 
                            "Wolff step did not change any site in the grid.")
        
        # Check that the cluster size returned is a positive integer
        self.assertIsInstance(cluster_size, int, "Cluster size is not an integer.")
        self.assertGreater(cluster_size, 0, "Cluster size should be greater than zero.")
        # Importance: Validates that the Wolff step successfully forms and flips a cluster, 
        # which is essential for the dynamics of the Potts model.

    def test_color_bar_creation(self):
        """Test to verify if a color bar is present in the plot created by simulate_potts."""
        
        # Custom parameters for testing
        L = 50  # Define a larger lattice size for more comprehensive testing
        q = 3   # Number of Potts states
        beta = 0.6  # Inverse temperature for interaction strength
        steps = 100  # Number of Monte Carlo iterations to simulate
        
        # Patch plt.show to avoid actual plotting during the test
        with patch('matplotlib.pyplot.show'):
            # Run the simulation, which should plot the grid and create a color bar
            simulate_potts(L, q, beta, steps)
            
            # Get the current figure to inspect its axes
            fig = plt.gcf()
            
            # Check if any of the axes is a color bar
            colorbar_found = any(isinstance(ax, plt.Axes) and 'colorbar' in ax.get_label().lower() for ax in fig.axes)
            
            # Assert that the color bar was found in the plot
            self.assertTrue(colorbar_found, "Color bar was not found in the plot.")
            
            # Clean up the plot to avoid memory issues
            plt.close()
        # Importance: Ensures that the color bar is created during the plotting process, 
        # which is crucial for visualizing the results of the Potts model simulation.

    def test_checking_simulate_potts_for_small_step(self):
        """Test to verify the creation of color bar in Potts model visualization."""
        L = 5  # Define a smaller grid for quick testing
        q = 3  # Number of Potts states
        beta = 0.4  # Inverse temperature
        steps = 1  # Simulate only a single step for quick validation
        
        # Patch plt.show to avoid actual plotting during the test
        with patch('matplotlib.pyplot.show'):
            # Run the simulation for a single step
            simulate_potts(L, q, beta, steps)
            plt.close()  # Close the figure to clean up

        # Importance: This test ensures that even for a minimal number of steps, the function behaves correctly 
        # and creates the expected visualization elements, such as the color bar.

if __name__ == "__main__":
    unittest.main(verbosity=2)
