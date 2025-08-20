import math
from datetime import datetime, timedelta

class Ride:
    def __init__(self, id, pickup_time, dropoff_time, pickup_location, dropoff_location):
        self.id = id
        self.pickup_time = pickup_time  # datetime object
        self.dropoff_time = dropoff_time  # datetime object
        self.pickup_location = pickup_location  # (latitude, longitude)
        self.dropoff_location = dropoff_location  # (latitude, longitude)

class Driver:
    def __init__(self, id, rate):
        self.id = id
        self.rate = rate  # hourly rate
        self.schedule = []  # List of assigned rides

def calculate_distance(loc1, loc2):
    lat1, lon1 = loc1
    lat2, lon2 = loc2
    return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)

def can_assign_ride(driver, ride):
    for scheduled_ride in driver.schedule:
        latest_pickup = max(ride.pickup_time, scheduled_ride.pickup_time)
        earliest_dropoff = min(ride.dropoff_time, scheduled_ride.dropoff_time)
        if latest_pickup < earliest_dropoff:
            return False  # There is a time overlap
    return True  # No overlap, ride can be assigned

def assign_rides(rides, drivers):
    rides.sort(key=lambda x: x.pickup_time)  # Sort rides by pickup time
    drivers.sort(key=lambda x: x.rate)  # Sort drivers by rate to prioritize lower-rate drivers

    for ride in rides:
        assigned = False
        for driver in drivers:
            if can_assign_ride(driver, ride):
                driver.schedule.append(ride)
                assigned = True
                break  # Ride assigned, move to the next ride
        if not assigned:
            print(f"Ride {ride.id} could not be assigned to any driver.")
    # Create and return a dict of driver schedules for easy access
    return {driver.id: driver.schedule for driver in drivers}

def optimize_routes(assignments):
    # Optimize each driver's schedule individually
    for driver_id, rides in assignments.items():
        if len(rides) <= 1:
            continue  # No optimization needed for 0 or 1 ride

        # Sort rides by pickup time initially
        rides.sort(key=lambda x: x.pickup_time)
        optimized_schedule = [rides.pop(0)]  # Start with the earliest ride

        while rides:
            last_ride = optimized_schedule[-1]
            # Find the next ride with the minimal distance from the last ride's dropoff location
            next_ride = min(rides, key=lambda r: calculate_distance(last_ride.dropoff_location, r.pickup_location))
            optimized_schedule.append(next_ride)
            rides.remove(next_ride)

        assignments[driver_id] = optimized_schedule
    return assignments

def main(rides, drivers):
    assignments = assign_rides(rides, drivers)
    optimized_assignments = optimize_routes(assignments)

    for driver in drivers:
        print(f"Driver {driver.id} (Rate: ${driver.rate:.1f}/hour):")
        sorted_rides = sorted(driver.schedule, key=lambda r: r.pickup_time)
        for ride in sorted_rides:
            print(f"  Ride {ride.id}: {ride.pickup_time.strftime('%Y-%m-%d %H:%M:%S')} to {ride.dropoff_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if not sorted_rides:
            print("  No assigned rides.")

if __name__ == "__main__":
    rides = [
        Ride(1, datetime(2023, 5, 1, 9, 0), datetime(2023, 5, 1, 9, 30), (40.7128, -74.0060), (40.730610, -73.935242)),
        Ride(2, datetime(2023, 5, 1, 9, 15), datetime(2023, 5, 1, 9, 45), (40.758896, -73.985130), (40.706192, -74.008874)),
        Ride(3, datetime(2023, 5, 1, 10, 0), datetime(2023, 5, 1, 10, 45), (40.730610, -73.935242), (40.758896, -73.985130)),
        Ride(4, datetime(2023, 5, 1, 10, 30), datetime(2023, 5, 1, 11, 15), (40.706192, -74.008874), (40.7128, -74.77))]
import math
from datetime import datetime, timedelta

class Ride:
    def __init__(self, id, pickup_time, dropoff_time, pickup_location, dropoff_location):
        self.id = id
        self.pickup_time = pickup_time  # datetime object
        self.dropoff_time = dropoff_time  # datetime object
        self.pickup_location = pickup_location  # (latitude, longitude)
        self.dropoff_location = dropoff_location  # (latitude, longitude)

class Driver:
    def __init__(self, id, rate):
        self.id = id
        self.rate = rate  # hourly rate
        self.schedule = []  # List of assigned rides

def calculate_distance(loc1, loc2):
    lat1, lon1 = loc1
    lat2, lon2 = loc2
    return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)

def can_assign_ride(driver, ride):
    for scheduled_ride in driver.schedule:
        latest_pickup = max(ride.pickup_time, scheduled_ride.pickup_time)
        earliest_dropoff = min(ride.dropoff_time, scheduled_ride.dropoff_time)
        if latest_pickup < earliest_dropoff:
            return False  # There is a time overlap
    return True  # No overlap, ride can be assigned

def assign_rides(rides, drivers):
    rides.sort(key=lambda x: x.pickup_time)  # Sort rides by pickup time
    drivers.sort(key=lambda x: x.rate)  # Sort drivers by rate to prioritize lower-rate drivers

    for ride in rides:
        assigned = False
        for driver in drivers:
            if can_assign_ride(driver, ride):
                driver.schedule.append(ride)
                assigned = True
                break  # Ride assigned, move to the next ride
        if not assigned:
            print(f"Ride {ride.id} could not be assigned to any driver.")
    # Create and return a dict of driver schedules for easy access
    return {driver.id: driver.schedule for driver in drivers}

def optimize_routes(assignments):
    # Optimize each driver's schedule individually
    for driver_id, rides in assignments.items():
        if len(rides) <= 1:
            continue  # No optimization needed for 0 or 1 ride

        # Sort rides by pickup time initially
        rides.sort(key=lambda x: x.pickup_time)
        optimized_schedule = [rides.pop(0)]  # Start with the earliest ride

        while rides:
            last_ride = optimized_schedule[-1]
            # Find the next ride with the minimal distance from the last ride's dropoff location
            next_ride = min(rides, key=lambda r: calculate_distance(last_ride.dropoff_location, r.pickup_location))
            optimized_schedule.append(next_ride)
            rides.remove(next_ride)

        assignments[driver_id] = optimized_schedule
    return assignments

def main(rides, drivers):
    assignments = assign_rides(rides, drivers)
    optimized_assignments = optimize_routes(assignments)

    for driver in drivers:
        print(f"Driver {driver.id} (Rate: ${driver.rate:.1f}/hour):")
        sorted_rides = sorted(driver.schedule, key=lambda r: r.pickup_time)
        for ride in sorted_rides:
            print(f"  Ride {ride.id}: {ride.pickup_time.strftime('%Y-%m-%d %H:%M:%S')} to {ride.dropoff_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if not sorted_rides:
            print("  No assigned rides.")

if __name__ == "__main__":
    rides = [
        Ride(1, datetime(2023, 5, 1, 9, 0), datetime(2023, 5, 1, 9, 30), (40.7128, -74.0060), (40.730610, -73.935242)),
        Ride(2, datetime(2023, 5, 1, 9, 15), datetime(2023, 5, 1, 9, 45), (40.758896, -73.985130), (40.706192, -74.008874)),
        Ride(3, datetime(2023, 5, 1, 10, 0), datetime(2023, 5, 1, 10, 45), (40.730610, -73.935242), (40.758896, -73.985130)),
        Ride(4, datetime(2023, 5, 1, 10, 30), datetime(2023, 5, 1, 11, 15), (40.706192, -74.008874), (40.7128, -74))]
