# Simulator Module
import simpy
from model.airbase_model import Aircraft


LAND_TIME = 3
REFUEL_TIME = 8
REARM_TIME = 10
TAKEOFF_TIME = 2


class AirbaseSimulation:

    def __init__(self, env):

        self.env = env

        # resources
        self.runway = simpy.Resource(env, capacity=1)
        self.fuel_truck = simpy.Resource(env, capacity=2)
        self.weapon_team = simpy.Resource(env, capacity=1)

    def aircraft_process(self, aircraft):

        print(f"{self.env.now}: {aircraft.name} requesting landing")

        # landing
        with self.runway.request() as req:
            yield req
            print(f"{self.env.now}: {aircraft.name} landing")
            yield self.env.timeout(LAND_TIME)

        # refueling
        with self.fuel_truck.request() as req:
            yield req
            print(f"{self.env.now}: {aircraft.name} refueling")
            yield self.env.timeout(REFUEL_TIME)

        # rearming
        with self.weapon_team.request() as req:
            yield req
            print(f"{self.env.now}: {aircraft.name} rearming")
            yield self.env.timeout(REARM_TIME)

        # takeoff
        with self.runway.request() as req:
            yield req
            print(f"{self.env.now}: {aircraft.name} taking off")
            yield self.env.timeout(TAKEOFF_TIME)

        print(f"{self.env.now}: {aircraft.name} departed")