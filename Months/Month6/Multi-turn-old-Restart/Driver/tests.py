import unittest
from datetime import datetime, timedelta
from testable import Location, RideAllocationSystem, Driver, Ride

class TestRideAllocationSystem(unittest.TestCase):
    
    def setUp(self):
        # Set up test data
        # Create test locations
        self.lax = Location(33.9416, -118.4085, "LAX Airport")
        self.hollywood = Location(34.1016, -118.3267, "Hollywood Blvd")
        self.santa_monica = Location(34.0195, -118.4912, "Santa Monica")
        
        # Create test drivers
        self.driver1 = Driver("D1", 20.0)  # $20/hour
        self.driver2 = Driver("D2", 25.0)  # $25/hour
        
        # Create test system
        self.system = RideAllocationSystem([self.driver1, self.driver2])
        
    def test_no_overlap(self):
        # It tests that rides don't overlap for the same driver.
        # Create overlapping rides
        ride1 = Ride(
            "R1",
            datetime(2024, 2, 12, 10, 0),  # 10:00 AM
            self.hollywood,
            self.lax,
            timedelta(minutes=45)
        )
        
        ride2 = Ride(
            "R2",
            datetime(2024, 2, 12, 10, 30),  # 10:30 AM (overlaps with ride1)
            self.santa_monica,
            self.hollywood,
            timedelta(minutes=30)
        )
        
        # Allocate rides
        allocations = self.system.allocate_rides([ride1, ride2])
        
        # Check that rides were allocated to different drivers
        self.assertNotEqual(
            allocations["D1"],
            allocations["D2"],
            "Overlapping rides should be allocated to different drivers"
        )
        
    def test_rate_priority(self):
        # It tests that lower rate drivers are prioritized.
        # Create non-overlapping rides
        ride1 = Ride(
            "R1",
            datetime(2024, 2, 12, 10, 0),
            self.hollywood,
            self.lax,
            timedelta(minutes=45)
        )
        
        ride2 = Ride(
            "R2",
            datetime(2024, 2, 12, 11, 0),  # No overlap
            self.santa_monica,
            self.hollywood,
            timedelta(minutes=30)
        )
        
        # Allocate rides
        allocations = self.system.allocate_rides([ride1, ride2])
        
        # Check that lower rate driver (driver1) got both rides
        self.assertEqual(len(allocations["D1"]), 2,
                        "Lower rate driver should get both non-overlapping rides")
        self.assertEqual(len(allocations["D2"]), 0,
                        "Higher rate driver should not get any rides")
        
    def test_geographic_efficiency(self):
        # It tests that geographic efficiency is considered.
        # Create rides that end and start at the same location
        ride1 = Ride(
            "R1",
            datetime(2024, 2, 12, 10, 0),
            self.hollywood,
            self.lax,
            timedelta(minutes=45)
        )
        
        ride2 = Ride(
            "R2",
            datetime(2024, 2, 12, 11, 0),
            self.lax,  # Starts where ride1 ends
            self.santa_monica,
            timedelta(minutes=30)
        )
        
        # Allocate rides
        allocations = self.system.allocate_rides([ride1, ride2])
        
        # Check that same driver got both rides
        driver_with_both = None
        for driver_id, rides in allocations.items():
            if len(rides) == 2:
                driver_with_both = driver_id
                break
                
        self.assertIsNotNone(driver_with_both,
                            "Geographically efficient rides should be assigned to same driver")

if __name__ == '__main__':
    unittest.main(verbosity=2)