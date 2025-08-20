import unittest
from plotly.graph_objects import Figure
from testableIC import create_candlestick_chart
class TestCandlestickChart(unittest.TestCase):
    
    def setUp(self):
        # Sample data for testing
        self.data = {
            'Date': ['2024-08-01', '2024-08-02', '2024-08-03', '2024-08-04', '2024-08-05'],
            'Open': [100, 102, 101, 104, 103],
            'High': [105, 106, 103, 108, 107],
            'Low': [98, 99, 100, 101, 102],
            'Close': [104, 101, 102, 107, 106]
        }
    
    def test_no_error_on_chart_creation(self):
        try:
            fig = create_candlestick_chart(self.data)
        except:
            self.fail(f"create_candlestick_chart raised an exception")

    def test_chart_is_created(self):
        try:
            fig = create_candlestick_chart(self.data)
            self.assertIsInstance(fig, Figure, "The chart is not created properly. It should be an instance of plotly.graph_objects.Figure")
        except:
            self.fail(f"candle stick chart creation failed!")

if __name__ == '__main__':
    unittest.main(verbosity=2)
