import unittest
from unittest.mock import patch
import matplotlib.pyplot as plt
from ideal_completion import generate_and_plot_3d  

class Test3DPlot(unittest.TestCase):

    @patch('matplotlib.pyplot.show')  # Mock plt.show() to prevent it from blocking
    def setUp(self, mock_show):
        # Run the imported plot function
        generate_and_plot_3d()

        # Retrieve the active figure and axes for further tests
        self.fig = plt.gcf()
        self.ax = self.fig.gca()

    def tearDown(self):
        """Ensure the plot is closed after each test to free resources."""
        plt.close(self.fig)

    def test_colorbar_present(self):
        """Test if the colorbar is present in the plot by checking for Axes object."""
        # Get all axes of the figure
        all_axes = self.fig.get_axes()

        # Colorbars in matplotlib are added as Axes objects.
        # Check if any of the axes in the figure correspond to a colorbar.
        colorbar_axes = [ax for ax in all_axes if ax.get_label() == '<colorbar>']

 
        # Assert that at least one colorbar exists in the figure
        self.assertGreater(len(colorbar_axes), 0, "Colorbar is not present in the plot")


    def test_axis_labels(self):
        """Test if the plot has correct axis labels."""
        self.assertEqual(self.ax.get_xlabel(), 'X', "X label is incorrect")
        self.assertEqual(self.ax.get_ylabel(), 'Y', "Y label is incorrect")
        self.assertEqual(self.ax.get_zlabel(), 'Z', "Z label is incorrect")

    def test_axis_limits(self):
        """Test if the plot has correct limits for each axis."""
        x_limits = self.ax.get_xlim()
        y_limits = self.ax.get_ylim()
        z_limits = self.ax.get_zlim()

        self.assertEqual(x_limits, (0, 10), "X-axis limits are incorrect")
    
        # Use delta to account for small floating point differences
        self.assertAlmostEqual(y_limits[0], -1, delta=0.001, msg="Y-axis lower limit is incorrect")
        self.assertAlmostEqual(y_limits[1], 1, delta=0.001, msg="Y-axis upper limit is incorrect")
        self.assertAlmostEqual(z_limits[0], -1, delta=0.001, msg="Z-axis lower limit is incorrect")
        self.assertAlmostEqual(z_limits[1], 1, delta=0.001, msg="Z-axis upper limit is incorrect")


if __name__ == "__main__":
    unittest.main(verbosity=2)
