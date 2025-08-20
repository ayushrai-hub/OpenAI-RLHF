from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict
from math import radians, sin, cos, sqrt, atan2

@dataclass
class Location:
    latitude: float
    longitude: float
    address: str

    def distance_to(self, other: 'Location') -> float:
        R = 6371.0  # Radius of the Earth in km
        lat1, lon1, lat2, lon2 = map(radians, [self.latitude, self.longitude, other.latitude, other.longitude])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

@dataclass
class Ride:
    id: str
    pickup_time: datetime
    pickup_location: Location
    dropoff_location: Location
    duration: timedelta

    @property
    def dropoff_time(self) -> datetime:
        return self.pickup_time + self.duration

@dataclass
class Driver:
    id: str
    rate: float
    schedule: List[Ride] = None

    def __post_init__(self):
        if self.schedule is None:
            self.schedule = []

    def can_take_ride(self, ride: Ride) -> bool:
        for scheduled_ride in self.schedule:
            if not (ride.pickup_time >= scheduled_ride.dropoff_time or ride.dropoff_time <= scheduled_ride.pickup_time):
                return False
        return True

    def add_ride(self, ride: Ride) -> None:
        self.schedule.append(ride)

class RideAllocationSystem:
    def __init__(self, drivers: List[Driver]):
        self.drivers = drivers

    def allocate_rides(self, rides: List[Ride]) -> Dict[str, List[Ride]]:
        rides.sort(key=lambda ride: ride.pickup_time)
        self.drivers.sort(key=lambda driver: driver.rate)

        for ride in rides:
            for driver in self.drivers:
                if driver.can_take_ride(ride):
                    driver.add_ride(ride)
                    break

        return {driver.id: driver.schedule for driver in self.drivers}
