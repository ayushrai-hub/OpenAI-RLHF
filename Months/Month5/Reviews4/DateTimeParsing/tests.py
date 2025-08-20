import unittest
from ideal import calculate_days_difference

class TestTimeDifference(unittest.TestCase):

    def test_time_earlier(self):
        days = calculate_days_difference({'destinationEta': '2024-08-24T00:00:00+02:00'})
        self.assertEqual(days, 33)

    def test_time_later(self):
        days = calculate_days_difference({'destinationEta': '2024-09-24T00:00:00'})
        self.assertEqual(days, 2)

if __name__ == '__main__':
    unittest.main()