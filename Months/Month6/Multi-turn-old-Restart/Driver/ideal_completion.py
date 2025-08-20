from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict
from math import radians, sin, cos, sqrt, atan2

@dataclass
class Location:
    """Represents a geographic location with latitude and longitude."""
    latitude: float
    longitude: float
    address: str

    def distance_to(self, other: 'Location') -> float:
        """
        Calculate the distance between two locations using the Haversine formula.
        Returns distance in kilometers.
        """
        R = 6371  # Earth's radius in kilometers

        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other.latitude), radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c

@dataclass
class Ride:
    """Represents a ride request with pickup and dropoff details."""
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
    """Represents a driver with their hourly rate and schedule."""
    id: str
    rate: float
    schedule: List[Ride] = None

    def __post_init__(self):
        if self.schedule is None:
            self.schedule = []

    def can_take_ride(self, ride: Ride) -> bool:
        """Check if the driver can take a ride without schedule conflicts."""
        if not self.schedule:
            return True
            
        for scheduled_ride in self.schedule:
            # Check for overlap
            if (scheduled_ride.pickup_time <= ride.dropoff_time and 
                ride.pickup_time <= scheduled_ride.dropoff_time):
                return False
        return True

    def add_ride(self, ride: Ride) -> None:
        """Add a ride to the driver's schedule."""
        if not self.can_take_ride(ride):
            raise ValueError("Ride conflicts with existing schedule")
        self.schedule.append(ride)
        # Sort schedule by pickup time
        self.schedule.sort(key=lambda x: x.pickup_time)

class RideAllocationSystem:
    """Main system for allocating rides to drivers."""
    
    def __init__(self, drivers: List[Driver]):
        self.drivers = sorted(drivers, key=lambda x: x.rate)  # Sort by rate

    def allocate_rides(self, rides: List[Ride]) -> Dict[str, List[Ride]]:
        """
        Allocate rides to drivers optimizing for:
        1. No schedule overlaps
        2. Lowest rate drivers
        3. Geographic efficiency
        
        Returns a dictionary mapping driver IDs to their assigned rides.
        """
        # Sort rides by pickup time
        sorted_rides = sorted(rides, key=lambda x: x.pickup_time)
        allocations = {driver.id: [] for driver in self.drivers}
        
        for ride in sorted_rides:
            best_driver = None
            min_cost = float('inf')
            
            for driver in self.drivers:
                if not driver.can_take_ride(ride):
                    continue
                    
                # Calculate cost based on rate and geographic efficiency
                cost = driver.rate
                
                if driver.schedule:
                    # Add distance cost from last dropoff to new pickup
                    last_ride = driver.schedule[-1]
                    distance = last_ride.dropoff_location.distance_to(ride.pickup_location)
                    cost += distance * 0.1  
                
                if cost < min_cost:
                    min_cost = cost
                    best_driver = driver
            
            if best_driver:
                best_driver.add_ride(ride)
                allocations[best_driver.id].append(ride)
            else:
                raise ValueError(f"Could not allocate ride {ride.id}")
                
        return allocations
