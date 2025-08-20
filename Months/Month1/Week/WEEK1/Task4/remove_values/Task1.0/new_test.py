import unittest
from datetime import datetime, timedelta
from freezegun import freeze_time
from new_date import format_reminder  # Replace 'your_reminder_module' with the actual module name

class TestReminderParser(unittest.TestCase):
    @freeze_time(datetime.now())
    def test_time_only(self):
        result = format_reminder("Remind me to call John at 3 PM")
        self.assertEqual(result, "Reminder: Remind me to call John at " + str(datetime.now()))

    @freeze_time("2024-06-21 13:00:00")
    def test_tomorrow(self):
        result = format_reminder("I have a meeting tomorrow")
        self.assertEqual(result, "Reminder: I have a meeting at 2024-06-22 00:00:00")

    @freeze_time("2024-06-21 13:00:00")
    def test_next_monday(self):
        result = format_reminder("My doctor's appointment is next Monday")
        self.assertEqual(result, "Reminder: My doctor's appointment is at 2024-06-24 00:00:00")

    @freeze_time("2024-06-21 13:00:00")
    def test_relative_time(self):
        result = format_reminder("Remind me to check the oven in 10 minutes")
        self.assertEqual(result, "Reminder: Remind me to check the oven at 2024-06-21 13:10:00")



if __name__ == '__main__':
    unittest.main()