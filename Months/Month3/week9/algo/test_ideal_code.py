import unittest
from datetime import datetime, timedelta
from typing import List, Tuple

# Import all the classes and functions from your main script
from testable_ideal_completion import Ride, Driver, calculate_distance, can_assign_ride, assign_rides, optimize_routes, main

class TestRideAssignment(unittest.TestCase):
    # Set up common test data for all test methods
    def setUp(self):
        self.rides = [
            Ride(1, datetime(2023, 5, 1, 9, 0), datetime(2023, 5, 1, 9, 30), (34.0522, -118.2437), (33.9416, -118.4085)),
            Ride(2, datetime(2023, 5, 1, 9, 15), datetime(2023, 5, 1, 10, 0), (34.0522, -118.2437), (34.0522, -118.2437)),
            Ride(3, datetime(2023, 5, 1, 10, 0), datetime(2023, 5, 1, 10, 45), (33.9416, -118.4085), (34.1478, -118.1445)),
        ]
        self.drivers = [
            Driver(1, 20.0),
            Driver(2, 25.0),
            Driver(3, 22.0),
        ]
    # This test verifies that the distance calculation is accurate
    def test_calculate_distance(self):
        loc1 = (34.0522, -118.2437)
        loc2 = (33.9416, -118.4085)
        distance = calculate_distance(loc1, loc2)
        self.assertAlmostEqual(distance, 0.1985, places=4)
    # It checks if the function correctly determines ride assignment possibility
    def test_can_assign_ride(self):
        driver = Driver(1, 20.0)
        ride1 = Ride(1, datetime(2023, 5, 1, 9, 0), datetime(2023, 5, 1, 9, 30), (0, 0), (0, 0))
        ride2 = Ride(2, datetime(2023, 5, 1, 9, 15), datetime(2023, 5, 1, 10, 0), (0, 0), (0, 0))
        ride3 = Ride(3, datetime(2023, 5, 1, 10, 0), datetime(2023, 5, 1, 10, 45), (0, 0), (0, 0))

        self.assertTrue(can_assign_ride(driver, ride1))
        driver.schedule.append(ride1)
        self.assertFalse(can_assign_ride(driver, ride2))
        self.assertTrue(can_assign_ride(driver, ride3))
    # This test verifies that rides are assigned correctly based on driver availability and rates
    def test_assign_rides(self):
        assign_rides(self.rides, self.drivers)
        self.assertEqual(len(self.drivers[0].schedule), 2)  # Driver 1 (lowest rate) should have 2 rides
        self.assertEqual(len(self.drivers[1].schedule), 0)  # Driver 2 (highest rate) should have no rides
        self.assertEqual(len(self.drivers[2].schedule), 1)  # Driver 3 should have 1 ride
    # This test checks if routes are optimized to minimize travel distance between rides
    def test_optimize_routes(self):
        assign_rides(self.rides, self.drivers)
        optimize_routes(self.drivers)
        
        # Check if Driver 1's schedule is optimized (Ride 1 followed by Ride 3)
        self.assertEqual(self.drivers[0].schedule[0].id, 1)
        self.assertEqual(self.drivers[0].schedule[1].id, 3)
    # This test verifies that the main function produces correct and readable information to end-users
    def test_main_output(self):
        import io
        import sys

        # Redirect stdout to capture print output
        captured_output = io.StringIO()
        sys.stdout = captured_output

        main(self.rides, self.drivers)

        # Restore stdout
        sys.stdout = sys.__stdout__

        expected_output = """Driver 1 (Rate: $20.0/hour):
  Ride 1: 2023-05-01 09:00:00 to 2023-05-01 09:30:00
  Ride 3: 2023-05-01 10:00:00 to 2023-05-01 10:45:00

Driver 2 (Rate: $25.0/hour):

Driver 3 (Rate: $22.0/hour):
  Ride 2: 2023-05-01 09:15:00 to 2023-05-01 10:00:00

"""
        self.assertEqual(captured_output.getvalue(), expected_output)

if __name__ == '__main__':
    unittest.main(verbosity=2)