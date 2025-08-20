import unittest
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent
import numpy as np

# Import the main script functions (assuming they're in a file named coordinate_picker.py)
from original import onclick, coordinates

class TestCoordinatePicker(unittest.TestCase):

    def setUp(self):
        self.fig, self.ax = plt.subplots()
        self.ax.imshow(np.random.rand(10, 10))
        self.coordinates = {}

    def tearDown(self):
        plt.close(self.fig)

    def simulate_click(self, x, y):
        event = MouseEvent('button_press_event', self.fig.canvas, x, y)
        event.inaxes = self.ax  # Simulate click inside axes
        onclick(event)

    def test_onclick_adds_coordinates(self):
        self.simulate_click(3.2, 4.7)
        self.assertIn((3, 5), self.coordinates)
        self.assertEqual(self.coordinates[(3, 5)], (3, 5))

    def test_onclick_rounds_coordinates(self):
        self.simulate_click(3.6, 4.1)
        self.assertIn((4, 4), self.coordinates)
        self.assertEqual(self.coordinates[(4, 4)], (4, 4))

    def test_multiple_clicks(self):
        clicks = [(1.2, 2.3), (4.5, 5.6), (7.8, 8.9)]
        for x, y in clicks:
            self.simulate_click(x, y)
        
        self.assertEqual(len(self.coordinates), 3)
        self.assertIn((1, 2), self.coordinates)
        self.assertIn((5, 6), self.coordinates)
        self.assertIn((8, 9), self.coordinates)

    def test_click_outside_axes(self):
        initial_len = len(self.coordinates)
        event = MouseEvent('button_press_event', self.fig.canvas, -1, -1)
        event.inaxes = None  # Simulate click outside axes
        onclick(event)
        self.assertEqual(len(self.coordinates), initial_len)

if __name__ == '__main__':
    unittest.main(verbosity=2)