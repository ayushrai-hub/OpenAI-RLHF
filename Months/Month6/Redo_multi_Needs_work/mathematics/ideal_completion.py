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
            return False
    return True

def assign_rides(rides, drivers):
    rides.sort(key=lambda x: x.pickup_time)
    drivers.sort(key=lambda x: x.rate)
    assignments = {}
    for ride in rides:
        assigned = False
        for driver in drivers:
            if can_assign_ride(driver, ride):
                driver.schedule.append(ride)
                if driver.id not in assignments:
                    assignments[driver.id] = []
                assignments[driver.id].append(ride)
                assigned = True
                break
        if not assigned:
            print(f"Ride {ride.id} could not be assigned to any driver.")
    return assignments

def optimize_routes(assignments):
    for driver_id, rides in assignments.items():
        rides.sort(key=lambda x: x.pickup_time)
        optimized_rides = []
        remaining_rides = rides.copy()
        current_location = None
        while remaining_rides:
            if current_location is None:
                next_ride = remaining_rides.pop(0)
            else:
                next_ride = min(remaining_rides, key=lambda ride: calculate_distance(current_location, ride.pickup_location))
                remaining_rides.remove(next_ride)
            optimized_rides.append(next_ride)
            current_location = next_ride.dropoff_location
        assignments[driver_id] = optimized_rides
    return assignments

def main():
    rides = [
        Ride(1, datetime(2023, 12, 23, 8, 0), datetime(2023, 12, 23, 9, 0), (40.7128, -74.0060), (40.730610, -73.935242)),
        Ride(2, datetime(2023, 12, 23, 8, 30), datetime(2023, 12, 23, 9, 30), (40.758896, -73.985130), (40.706192, -74.008874)),
        Ride(3, datetime(2023, 12, 23, 9, 0), datetime(2023, 12, 23, 10, 0), (40.730610, -73.935242), (40.758896, -73.985130)),
        Ride(4, datetime(2023, 12, 23, 9, 30), datetime(2023, 12, 23, 10, 30), (40.706192, -74.008874), (40.7128, -74.0060)),
    ]

    drivers = [
        Driver(1, 20),  # $20/hour
        Driver(2, 15),  # $15/hour
        Driver(3, 25),  # $25/hour
    ]

    assignments = assign_rides(rides, drivers)
    optimized_assignments = optimize_routes(assignments)

    for driver_id, rides in optimized_assignments.items():
        total_hours = sum([(ride.dropoff_time - ride.pickup_time).total_seconds() / 3600 for ride in rides])
        total_cost = total_hours * next(driver.rate for driver in drivers if driver.id == driver_id)
        ride_ids = ', '.join(str(ride.id) for ride in rides)
        print(f"Driver {driver_id}: Rides [{ride_ids}], Total Hours: {total_hours:.2f}, Total Cost: ${total_cost:.2f}")

if __name__ == "__main__":
    main()
