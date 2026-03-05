# Main entry point for Airbase Digital Twin
from model.airbase_model import Airbase, Aircraft

def main():

    base = Airbase()

    jet1 = Aircraft("Jet-1", priority=1)
    jet2 = Aircraft("Jet-2", priority=2)

    base.add_aircraft(jet1)
    base.add_aircraft(jet2)

    print("Airbase Aircraft:")
    print(base.get_status())


if __name__ == "__main__":
    main()