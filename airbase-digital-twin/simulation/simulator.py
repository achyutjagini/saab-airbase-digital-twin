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

    def __init__(self, env):

        self.env = env

        # resources
        self.runway = simpy.Resource(env, capacity=1)
        self.fuel_truck = simpy.Resource(env, capacity=2)
        self.weapon_team = simpy.Resource(env, capacity=1)

    def aircraft_process(self, aircraft):

        print(f"{self.env.now}: {aircraft.name} requesting landing")

        # Landing
        with self.runway.request() as req:
            yield req
            print(f"{self.env.now}: {aircraft.name} landing")
            yield self.env.timeout(LAND_TIME)

        # Refueling
        with self.fuel_truck.request() as req:
            yield req

            while satellite_overhead(self.env.now):
                print(f"{self.env.now}: Satellite overhead, delaying refuel for {aircraft.name}")
                yield self.env.timeout(1)

            print(f"{self.env.now}: {aircraft.name} refueling")
            yield self.env.timeout(REFUEL_TIME)

        # Rearming
        with self.weapon_team.request() as req:
            yield req

            while satellite_overhead(self.env.now):
                print(f"{self.env.now}: Satellite overhead, delaying rearm for {aircraft.name}")
                yield self.env.timeout(1)

            print(f"{self.env.now}: {aircraft.name} rearming")
            yield self.env.timeout(REARM_TIME)

        # Takeoff
        with self.runway.request() as req:
            yield req
            print(f"{self.env.now}: {aircraft.name} taking off")
            yield self.env.timeout(TAKEOFF_TIME)

        print(f"{self.env.now}: {aircraft.name} departed")