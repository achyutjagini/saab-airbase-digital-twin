# Airbase Model Module

class Aircraft:
    def __init__(self, name, priority=1):
        self.name = name
        self.priority = priority
        self.status = "waiting"

    def __repr__(self):
        return f"{self.name} ({self.status})"


class Airbase:
    def __init__(self):

        # resources
        self.runways = 1
        self.fuel_trucks = 2
        self.weapon_crews = 1

        # aircraft list
        self.aircraft = []

    def add_aircraft(self, aircraft):
        self.aircraft.append(aircraft)

    def get_status(self):
        return [str(a) for a in self.aircraft]