import unittest
from matplotlib.backend_bases import MouseEvent
from slope import main  # Assuming the above code is saved as coordinate_picker.py

class TestCoordinatePicker(unittest.TestCase):
    def setUp(self):
        self.picker = main()

    def test_onclick_inside_axes(self):
        # Simulate a click inside the axes
        event = MouseEvent('button_press_event', self.picker.fig.canvas, 5, 5)
        event.inaxes = self.picker.ax
        result = self.picker.onclick(event)
        self.assertIsNotNone(result)
        self.assertEqual(len(self.picker.get_coordinates()), 1)

    def test_onclick_outside_axes(self):
        # Simulate a click outside the axes
        event = MouseEvent('button_press_event', self.picker.fig.canvas, -1, -1)
        event.inaxes = None
        result = self.picker.onclick(event)
        self.assertIsNone(result)
        self.assertEqual(len(self.picker.get_coordinates()), 0)

    def test_multiple_clicks(self):
        # Simulate multiple clicks
        for i in range(5):
            event = MouseEvent('button_press_event', self.picker.fig.canvas, i, i)
            event.inaxes = self.picker.ax
            self.picker.onclick(event)
        self.assertEqual(len(self.picker.get_coordinates()), 5)

    def test_coordinate_values(self):
        # Test if the stored coordinates match the click positions
        event = MouseEvent('button_press_event', self.picker.fig.canvas, 3, 7)
        event.inaxes = self.picker.ax
        x, y = self.picker.onclick(event)
        stored_coords = self.picker.get_coordinates()
        self.assertIn((x, y), stored_coords)
        self.assertEqual(stored_coords[(x, y)], (x, y))

if __name__ == '__main__':
    unittest.main(verbosity=2)