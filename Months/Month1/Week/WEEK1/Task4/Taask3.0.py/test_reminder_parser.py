import unittest
from datetime import datetime, timedelta
from reminder_parser import parse_reminder 

class TestParseReminder(unittest.TestCase):
    def setUp(self):
        self.base_date = datetime.now()  

    def test_am_pm_time(self):
        message, time = parse_reminder("Remind me to call John at 3 PM", self.base_date)
        self.assertEqual(message, "Remind me to call John")
        self.assertEqual(time, "15:00:00")

    def test_in_minutes(self):
        message, time = parse_reminder("Check oven in 10 minutes", self.base_date)
        expected_time = (self.base_date + timedelta(minutes=10)).strftime('%H:%M:%S')
        self.assertEqual(message, "Check oven")
        self.assertEqual(time, expected_time)

    def test_tomorrow(self):
        message, time = parse_reminder("I have a meeting tomorrow", self.base_date)
        expected_date = (self.base_date + timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')
        self.assertEqual(message, "I have a meeting")
        self.assertEqual(time, expected_date)

    def test_next_monday(self):
        message, time = parse_reminder("My doctor's appointment is next Monday", self.base_date)
        days_ahead = 7 - self.base_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        expected_date = (self.base_date + timedelta(days=days_ahead)).strftime('%Y-%m-%d 00:00:00')
        self.assertEqual(message, "My doctor's appointment is")
        self.assertEqual(time, expected_date)

if __name__ == '__main__':
    unittest.main(verbosity=2)