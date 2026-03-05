import sys
import os
import streamlit as st
import simpy

# add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.simulator import AirbaseSimulation
from model.airbase_model import Aircraft


st.title("✈️ Airbase Digital Twin")

env = simpy.Environment()
sim = AirbaseSimulation(env)

aircraft_list = [
    Aircraft("Jet-1"),
    Aircraft("Jet-2"),
    Aircraft("Jet-3")
]

for aircraft in aircraft_list:
    env.process(sim.aircraft_process(aircraft))

env.run()

st.header("Simulation Events")

for event in sim.events:
    st.text(event)