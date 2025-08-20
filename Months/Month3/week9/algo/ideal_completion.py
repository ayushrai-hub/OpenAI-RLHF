from datetime import datetime, timedelta
from typing import List, Tuple
import heapq

class Ride:
    def __init__(self, id: int, pickup_time: datetime, dropoff_time: datetime, 
                 pickup_location: Tuple[float, float], dropoff_location: Tuple[float, float]):
        self.id = id
        self.pickup_time = pickup_time
        self.dropoff_time = dropoff_time
        self.pickup_location = pickup_location
        self.dropoff_location = dropoff_location

class Driver:
    def __init__(self, id: int, rate: float):
        self.id = id
        self.rate = rate
        self.schedule: List[Ride] = []

def calculate_distance(loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
    # Simple Euclidean distance calculation
    return ((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2) ** 0.5

def can_assign_ride(driver: Driver, new_ride: Ride) -> bool:
    # Check if the new ride doesn't overlap with any existing rides in the driver's schedule
    for ride in driver.schedule:
        if ride.pickup_time < new_ride.dropoff_time and new_ride.pickup_time < ride.dropoff_time:
            return False
    return True

def assign_rides(rides: List[Ride], drivers: List[Driver]):
    # Sort rides by pickup time
    rides.sort(key=lambda x: x.pickup_time)
    
    # Create a min-heap of drivers based on their rates
    driver_heap = [(driver.rate, driver) for driver in drivers]
    heapq.heapify(driver_heap)
    
    for ride in rides:
        assigned = False
        temp_heap = []
        
        while driver_heap and not assigned:
            _, driver = heapq.heappop(driver_heap)
            
            if can_assign_ride(driver, ride):
                driver.schedule.append(ride)
                assigned = True
            
            temp_heap.append((driver.rate, driver))
        
        # Push back the drivers that weren't assigned this ride
        for driver_item in temp_heap:
            heapq.heappush(driver_heap, driver_item)
    
    # After assignment, sort each driver's schedule
    for driver in drivers:
        driver.schedule.sort(key=lambda x: x.pickup_time)

def optimize_routes(drivers: List[Driver]):
    for driver in drivers:
        optimized_schedule = []
        current_ride = None
        
        while driver.schedule:
            if not current_ride:
                current_ride = driver.schedule.pop(0)
                optimized_schedule.append(current_ride)
                continue
            
            best_next_ride = None
            best_distance = float('inf')
            
            for ride in driver.schedule:
                if ride.pickup_time >= current_ride.dropoff_time:
                    distance = calculate_distance(current_ride.dropoff_location, ride.pickup_location)
                    if distance < best_distance:
                        best_distance = distance
                        best_next_ride = ride
            
            if best_next_ride:
                optimized_schedule.append(best_next_ride)
                driver.schedule.remove(best_next_ride)
                current_ride = best_next_ride
            else:
                break
        
        driver.schedule = optimized_schedule

def main(rides: List[Ride], drivers: List[Driver]):
    assign_rides(rides, drivers)
    optimize_routes(drivers)
    
    # Print results
    for driver in drivers:
        print(f"Driver {driver.id} (Rate: ${driver.rate}/hour):")
        for ride in driver.schedule:
            print(f"  Ride {ride.id}: {ride.pickup_time} to {ride.dropoff_time}")
        print()

# Example usage
if __name__ == "__main__":
    rides = [
        Ride(1, datetime(2023, 5, 1, 9, 0), datetime(2023, 5, 1, 9, 30), (34.0522, -118.2437), (33.9416, -118.4085)),
        Ride(2, datetime(2023, 5, 1, 9, 15), datetime(2023, 5, 1, 10, 0), (34.0522, -118.2437), (34.0522, -118.2437)),
        Ride(3, datetime(2023, 5, 1, 10, 0), datetime(2023, 5, 1, 10, 45), (33.9416, -118.4085), (34.1478, -118.1445)),
    ]
    
    drivers = [
        Driver(1, 20.0),
        Driver(2, 25.0),
        Driver(3, 22.0),
    ]
    
    main(rides, drivers)