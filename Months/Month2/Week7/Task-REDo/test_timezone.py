import unittest
from datetime import datetime
import pytz
from unittest import mock

# Import the function to test
from testable_ideal_solution import convert_utc_to_est

class TestConvertUTCToEST(unittest.TestCase):
    def test_convert_utc_to_est(self):
        # Call the function
        utc_time, est_time = convert_utc_to_est()
        
        # Test that both returned values are datetime objects
        self.assertIsInstance(utc_time, datetime)
        self.assertIsInstance(est_time, datetime)
        
        # Test that UTC time has UTC timezone
        self.assertEqual(utc_time.tzinfo, pytz.UTC)
        
        # Test that EST time has US/Eastern timezone
        self.assertEqual(str(est_time.tzinfo), 'US/Eastern')
        
        # Test that the time difference is either 4 or 5 hours
        time_difference = utc_time - est_time.replace(tzinfo=pytz.UTC)
        self.assertIn(round(time_difference.total_seconds() / 3600), [4, 5])

   

    def test_time_consistency(self):
        utc_time1, est_time1 = convert_utc_to_est()
        utc_time2, est_time2 = convert_utc_to_est()
        
        # Test that the function returns current time (within 2 seconds)
        self.assertLess((utc_time2 - utc_time1).total_seconds(), 2)
        self.assertLess((est_time2 - est_time1).total_seconds(), 2)

if __name__ == '__main__':
    unittest.main(verbosity=2)