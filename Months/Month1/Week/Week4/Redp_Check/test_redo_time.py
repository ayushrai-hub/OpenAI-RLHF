import unittest
from dateparser import parse
from redo_check_time import parse_reminder

class TestParseReminder(unittest.TestCase):
    def test_specific_time(self):
        message, time = parse_reminder("Remind me to call John at 3 PM")
        self.assertEqual(message, "Remind me to call John")
        self.assertIsNotNone(time)
        self.assertEqual(time.hour, 15)
        self.assertEqual(time.minute, 0)

    def test_tomorrow(self):
        message, time = parse_reminder("I have a meeting tomorrow")
        self.assertEqual(message, "I have a meeting")
        self.assertIsNotNone(time)
        expected_date = parse('tomorrow').date()
        self.assertEqual(time.date(), expected_date)
        self.assertEqual(time.hour, 0)
        self.assertEqual(time.minute, 0)

    def test_next_day(self):
        message, time = parse_reminder("My doctor's appointment is next Monday")
        self.assertEqual(message, "My doctor's appointment is")
        self.assertIsNotNone(time)
        self.assertEqual(time.weekday(), 0)  # Monday is 0

    def test_relative_time(self):
        message, time = parse_reminder("Remind me to check the oven in 10 minutes")
        self.assertEqual(message, "Remind me to check the oven")
        self.assertIsNotNone(time)
        expected_time = parse('in 10 minutes')
        self.assertAlmostEqual(time.timestamp(), expected_time.timestamp(), delta=1)  # Allow 1 second difference

if __name__ == '__main__':
    unittest.main(verbosity=2)