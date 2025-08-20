
from typing import List, Tuple
from datetime import datetime

class Ride:
    def __init__(self, id: int, pickup_time: datetime, dropoff_time: datetime, pickup_location: Tuple[float, float], dropoff_location: Tuple[float, float]):
        self.id = id
        self.pickup_time = pickup_time
        self.dropoff_time = dropoff_time
        self.pickup_location = pickup_location
        self.dropoff_location = dropoff_location

class Driver:
    def __init__(self, id: int, rate: float):
        self.id = id
        self.rate = rate
        self.schedule = []  # list of rides

def calculate_distance(loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
    return ((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2) ** 0.5

def can_assign_ride(driver: Driver, new_ride: Ride) -> bool:
    for ride in driver.schedule:
        if ride.pickup_time < new_ride.dropoff_time and new_ride.pickup_time < ride.dropoff_time:
            return False
    return True

def assign_rides(rides: List[Ride], drivers: List[Driver]) -> None:
    rides.sort(key=lambda x: x.pickup_time)
    for ride in rides:
        drivers.sort(key=lambda x: x.rate)
        for driver in drivers:
            if can_assign_ride(driver, ride):
                driver.schedule.append(ride)
                break

def build_graph(rides: List[Ride]) -> dict:
    graph = {}
    for ride in rides:
        graph[ride] = []
        for next_ride in rides:
            if ride.dropoff_time <= next_ride.pickup_time:
                distance = calculate_distance(ride.dropoff_location, next_ride.pickup_location)
                graph[ride].append((next_ride, distance))
    return graph

def optimize_routes(drivers: List[Driver]) -> None:
    for driver in drivers:
        driver.schedule.sort(key=lambda ride: ride.pickup_time)

def main(rides: List[Ride], drivers: List[Driver]) -> None:
    assign_rides(rides, drivers)
    optimize_routes(drivers)
    for driver in drivers:
        print(f"Driver {driver.id} schedule:")
        for ride in driver.schedule:
            print(f"  Ride {ride.id} from {ride.pickup_location} to {ride.dropoff_location}")
