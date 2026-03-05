# Main entry point for Airbase Digital Twin
import simpy
from model.airbase_model import Aircraft
from simulation.simulator import AirbaseSimulation


def main():

    env = simpy.Environment()

    sim = AirbaseSimulation(env)

    aircraft_list = [
        Aircraft("Jet-1", priority=1),
        Aircraft("Jet-2", priority=2),
        Aircraft("Jet-3", priority=1)
    ]

    for aircraft in aircraft_list:
        env.process(sim.aircraft_process(aircraft))

    env.run()


if __name__ == "__main__":
    main()