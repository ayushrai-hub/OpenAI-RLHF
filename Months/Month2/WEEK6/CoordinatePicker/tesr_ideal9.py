import unittest
from unittest.mock import patch
import numpy as np
from original import CoordinatePicker  # Assume the above code is in coordinate_picker.py

class TestCoordinatePicker(unittest.TestCase):
    def setUp(self):
        self.picker = CoordinatePicker()

    def test_onclick(self):
        # Mock an event with x=3.2, y=4.7
        mock_event = type('MockEvent', (), {'xdata': 3.2, 'ydata': 4.7, 'inaxes': True})()
        
        self.picker.onclick(mock_event)
        
        self.assertEqual(self.picker.coordinates, {(3, 5): (3, 5)})

    def test_plot_and_pick(self):
        test_data = np.random.rand(5, 5)
        
        with patch('matplotlib.pyplot.show') as mock_show:
            with patch.object(self.picker, 'onclick') as mock_onclick:
                result = self.picker.plot_and_pick(test_data)
        
        mock_show.assert_called_once()
        self.assertEqual(result, self.picker.coordinates)

    def test_multiple_clicks(self):
        events = [
            type('MockEvent', (), {'xdata': 1.8, 'ydata': 2.3, 'inaxes': True})(),
            type('MockEvent', (), {'xdata': 3.2, 'ydata': 4.7, 'inaxes': True})(),
            type('MockEvent', (), {'xdata': 0.9, 'ydata': 1.1, 'inaxes': True})()
        ]
        
        for event in events:
            self.picker.onclick(event)
        
        expected = {(2, 2): (2, 2), (3, 5): (3, 5), (1, 1): (1, 1)}
        self.assertEqual(self.picker.coordinates, expected)

if __name__ == '__main__':
    unittest.main(verbosity=2)