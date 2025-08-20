import unittest
from datetime import datetime, timezone
from code import convert_utc_to_est

class TestTimezoneConversion(unittest.TestCase):
    def test_utc_to_est_conversion(self):
        utc_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        est_time = convert_utc_to_est(utc_time)
        
        self.assertEqual(est_time.year, 2023)
        self.assertEqual(est_time.month, 1)
        self.assertEqual(est_time.day, 1)
        self.assertIn(est_time.hour, [7, 8])
        self.assertEqual(est_time.minute, 0)
        self.assertEqual(est_time.second, 0)
        self.assertEqual(est_time.tzinfo.zone, 'US/Eastern')
    
    def test_dst_handling(self):
        summer_utc = datetime(2023, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
        summer_est = convert_utc_to_est(summer_utc)
        self.assertEqual(summer_est.hour, 8)
        
        winter_utc = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        winter_est = convert_utc_to_est(winter_utc)
        self.assertEqual(winter_est.hour, 7)

if __name__ == '__main__':
    unittest.main(verbosity=2)