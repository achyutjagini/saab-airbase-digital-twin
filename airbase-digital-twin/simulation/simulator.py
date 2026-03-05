# Simulator Module
import simpy
from model.airbase_model import Aircraft


# Satellite pass windows (simulation time)
SATELLITE_WINDOWS = [(10, 15), (40, 45)]

LAND_TIME = 3
REFUEL_TIME = 8
REARM_TIME = 10
TAKEOFF_TIME = 2


# Check if a satellite is overhead
def satellite_overhead(time):

    for start, end in SATELLITE_WINDOWS:
        if start <= time <= end:
            return True

    return False


class AirbaseSimulation:

    def __init__(self, env, fuel_truck_capacity=2, satellite_windows=None):

        self.env = env

        # resources
        self.runway = simpy.Resource(env, capacity=1)
        self.fuel_truck = simpy.Resource(env, capacity=fuel_truck_capacity)
        self.weapon_team = simpy.Resource(env, capacity=1)

        # satellite windows (use custom or default)
        self.satellite_windows = satellite_windows if satellite_windows is not None else SATELLITE_WINDOWS

        # state tracking
        self.events = []
        self.aircraft_states = {}
        self.resource_states = {
            "runway": {"capacity": 1, "in_use": 0},
            "fuel_truck": {"capacity": fuel_truck_capacity, "in_use": 0},
            "weapon_team": {"capacity": 1, "in_use": 0}
        }

    def satellite_overhead_check(self, time):
        """Check if satellite is overhead at given time"""
        for start, end in self.satellite_windows:
            if start <= time <= end:
                return True
        return False

    def log_event(self, aircraft_name, event, status="completed"):
        """Log a structured event"""
        self.events.append({
            "time": self.env.now,
            "aircraft": aircraft_name,
            "event": event,
            "status": status
        })

    def update_aircraft_state(self, aircraft, status, operation):
        """Update aircraft state tracking"""
        aircraft.status = status
        aircraft.current_operation = operation
        aircraft.start_time = self.env.now
        
        self.aircraft_states[aircraft.name] = {
            "status": status,
            "current_operation": operation,
            "start_time": self.env.now
        }

    def update_resource_state(self, resource_name, in_use):
        """Update resource utilization"""
        if resource_name in self.resource_states:
            self.resource_states[resource_name]["in_use"] = in_use

    def aircraft_process(self, aircraft):
        
        # Initialize aircraft state
        self.update_aircraft_state(aircraft, "waiting", "requesting_landing")
        self.log_event(aircraft.name, "requesting_landing", "waiting")
        print(f"{self.env.now}: {aircraft.name} requesting landing")

        # Landing
        with self.runway.request() as req:
            yield req
            self.update_resource_state("runway", 1)
            self.update_aircraft_state(aircraft, "landing", "landing")
            self.log_event(aircraft.name, "landing", "in_progress")
            print(f"{self.env.now}: {aircraft.name} landing")
            yield self.env.timeout(LAND_TIME)
            self.log_event(aircraft.name, "landing", "completed")
            self.update_resource_state("runway", 0)

        # Refueling
        with self.fuel_truck.request() as req:
            yield req
            self.update_resource_state("fuel_truck", len(self.fuel_truck.queue) + len(self.fuel_truck.users))

            # Check for satellite overhead
            while self.satellite_overhead_check(self.env.now):
                self.update_aircraft_state(aircraft, "waiting", "satellite_delay")
                self.log_event(aircraft.name, "satellite_delay", "waiting")
                print(f"{self.env.now}: Satellite overhead, delaying refuel for {aircraft.name}")
                yield self.env.timeout(1)

            self.update_aircraft_state(aircraft, "refueling", "refueling")
            self.log_event(aircraft.name, "refueling", "in_progress")
            print(f"{self.env.now}: {aircraft.name} refueling")
            yield self.env.timeout(REFUEL_TIME)
            self.log_event(aircraft.name, "refueling", "completed")
            self.update_resource_state("fuel_truck", len(self.fuel_truck.queue) + len(self.fuel_truck.users) - 1)

        # Rearming
        with self.weapon_team.request() as req:
            yield req
            self.update_resource_state("weapon_team", 1)

            # Check for satellite overhead
            while self.satellite_overhead_check(self.env.now):
                self.update_aircraft_state(aircraft, "waiting", "satellite_delay")
                self.log_event(aircraft.name, "satellite_delay", "waiting")
                print(f"{self.env.now}: Satellite overhead, delaying rearm for {aircraft.name}")
                yield self.env.timeout(1)

            self.update_aircraft_state(aircraft, "rearming", "rearming")
            self.log_event(aircraft.name, "rearming", "in_progress")
            print(f"{self.env.now}: {aircraft.name} rearming")
            yield self.env.timeout(REARM_TIME)
            self.log_event(aircraft.name, "rearming", "completed")
            self.update_resource_state("weapon_team", 0)

        # Takeoff
        with self.runway.request() as req:
            yield req
            self.update_resource_state("runway", 1)
            self.update_aircraft_state(aircraft, "taking_off", "takeoff")
            self.log_event(aircraft.name, "takeoff", "in_progress")
            print(f"{self.env.now}: {aircraft.name} taking off")
            yield self.env.timeout(TAKEOFF_TIME)
            self.log_event(aircraft.name, "takeoff", "completed")
            self.update_resource_state("runway", 0)

        self.update_aircraft_state(aircraft, "departed", "completed")
        self.log_event(aircraft.name, "departed", "completed")
        print(f"{self.env.now}: {aircraft.name} departed")
