import unittest
from unittest.mock import Mock, patch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as mcollections
from original import coordinates, onclick, data

class TestCoordinatePicker(unittest.TestCase):
    def setUp(self):
        self.fig, self.ax, self.scatter = create_plot(data)
        clear_coordinates()  # Clear coordinates before each test

    def tearDown(self):
        plt.close(self.fig)
    # This test verifies that the onclick function correctly handles a valid coordinate
    def test_onclick_valid_coordinate(self):

        event = Mock()
        event.inaxes = self.ax
        event.xdata = 2.4
        event.ydata = 3.6
        result = onclick(event, self.ax, self.scatter)

        self.assertIn((2, 4), result)
        self.assertEqual(result[(2, 4)], data[4, 2])
    # This test checks the onclick function's behavior when an out-of-bounds coordinate is clicked
    def test_onclick_out_of_bounds(self):
        event = Mock()
        event.inaxes = self.ax
        event.xdata = -1
        event.ydata = 11

        with patch('builtins.print') as mock_print:
            result = onclick(event, self.ax, self.scatter)

        mock_print.assert_called_with("Coordinate (-1, 11) is out of bounds")
        self.assertEqual(result, {})
    #s This test ensures that the onclick function correctly handles clicks on wrong axes
    def test_onclick_wrong_axes(self):
        event = Mock()
        event.inaxes = Mock()  # A different axes object
        event.xdata = 2
        event.ydata = 3

        result = onclick(event, self.ax, self.scatter)

        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main(verbosity=2)