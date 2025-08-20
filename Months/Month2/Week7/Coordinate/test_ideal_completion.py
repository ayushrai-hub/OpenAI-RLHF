import unittest
from unittest.mock import Mock, patch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as mcollections
from code_original import coordinates, data, onclick, create_plot
class TestCoordinatePicker(unittest.TestCase):

    def setUp(self):
        self.fig, self.ax, self.scatter = create_plot()
        clear_coordinates()  # Clear coordinates before each test

    def tearDown(self):
        plt.close(self.fig)

    def test_onclick_valid_coordinate(self):
        event = Mock()
        event.inaxes = self.ax
        event.xdata = 2.4
        event.ydata = 3.6

        result = onclick(event, self.ax, self.scatter)

        self.assertIn((2, 4), result)
        self.assertEqual(result[(2, 4)], data[4, 2])

    def test_onclick_out_of_bounds(self):
        event = Mock()
        event.inaxes = self.ax
        event.xdata = -1
        event.ydata = 11

        with patch('builtins.print') as mock_print:
            result = onclick(event, self.ax, self.scatter)

        mock_print.assert_called_with("Coordinate (-1, 11) is out of bounds")
        self.assertEqual(result, {})

    def test_onclick_invalid_coordinate(self):
        event = Mock()
        event.inaxes = self.ax
        event.xdata = None
        event.ydata = 'invalid'

        with patch('builtins.print') as mock_print:
            result = onclick(event, self.ax, self.scatter)

        mock_print.assert_called_with("Invalid coordinate values")
        self.assertEqual(result, {})

    def test_onclick_wrong_axes(self):
        event = Mock()
        event.inaxes = Mock()  # A different axes object
        event.xdata = 2
        event.ydata = 3

        result = onclick(event, self.ax, self.scatter)

        self.assertEqual(result, {})

    def test_create_plot(self):
        fig, ax, scatter = create_plot()

        self.assertIsInstance(fig, plt.Figure)
        self.assertIsInstance(ax, plt.Axes)
        self.assertIsInstance(scatter, mcollections.PathCollection)

        plt.close(fig)

    def test_multiple_clicks(self):
        event1 = Mock(inaxes=self.ax, xdata=1.5, ydata=2.5)
        event2 = Mock(inaxes=self.ax, xdata=3.5, ydata=4.5)

        result1 = onclick(event1, self.ax, self.scatter)
        result2 = onclick(event2, self.ax, self.scatter)

        self.assertIn((2, 2), result1)
        self.assertIn((4, 4), result2)
        self.assertEqual(len(result2), 2)

if __name__ == '__main__':
    unittest.main(verbosity=2)