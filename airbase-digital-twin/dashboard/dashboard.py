import sys
import os
import streamlit as st
import simpy
import pandas as pd

# add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.simulator import AirbaseSimulation, satellite_overhead, SATELLITE_WINDOWS
from model.airbase_model import Aircraft


# Page configuration
st.set_page_config(page_title="Airbase Digital Twin", page_icon="✈️", layout="wide")

st.title("✈️ Airbase Digital Twin")
st.markdown("**AI-Assisted Airbase Operations Planning**")

# Initialize session state
if 'simulation_run' not in st.session_state:
    st.session_state.simulation_run = False
    st.session_state.sim = None
    st.session_state.env = None
    st.session_state.num_aircraft = 3
    st.session_state.fuel_truck_capacity = 2
    st.session_state.satellite_windows = [(10, 15), (40, 45)]
    st.session_state.aircraft_counter = 3

# Sidebar for simulation controls
st.sidebar.header("Simulation Controls")

# Scenario configuration
st.sidebar.subheader("⚙️ Scenario Configuration")

num_aircraft = st.sidebar.number_input(
    "Number of Aircraft",
    min_value=1,
    max_value=10,
    value=st.session_state.num_aircraft,
    step=1
)

fuel_capacity = st.sidebar.selectbox(
    "Fuel Truck Capacity",
    options=[1, 2, 3],
    index=1,
    help="Simulate fuel truck failure by reducing capacity"
)

st.sidebar.divider()

# Run simulation button
if st.sidebar.button("🚀 Run Simulation", type="primary"):
    # Update session state
    st.session_state.num_aircraft = num_aircraft
    st.session_state.fuel_truck_capacity = fuel_capacity
    
    # Create new environment and simulation
    env = simpy.Environment()
    sim = AirbaseSimulation(
        env,
        fuel_truck_capacity=fuel_capacity,
        satellite_windows=st.session_state.satellite_windows
    )
    
    # Create aircraft
    aircraft_list = []
    for i in range(num_aircraft):
        priority = 1 if i % 2 == 0 else 2  # Alternate priorities
        aircraft_list.append(Aircraft(f"Jet-{i+1}", priority=priority))
    
    # Start aircraft processes
    for aircraft in aircraft_list:
        env.process(sim.aircraft_process(aircraft))
    
    # Run simulation
    env.run()
    
    # Store in session state
    st.session_state.simulation_run = True
    st.session_state.sim = sim
    st.session_state.env = env
    st.session_state.aircraft_counter = num_aircraft
    st.rerun()

# Interactive scenario buttons
st.sidebar.subheader("🎮 Interactive Scenarios")

if st.sidebar.button("➕ Add Aircraft"):
    if st.session_state.simulation_run:
        st.session_state.num_aircraft += 1
        st.sidebar.success(f"Added aircraft! Total: {st.session_state.num_aircraft}")
        st.sidebar.info("Click 'Run Simulation' to apply changes")

if st.sidebar.button("🛰️ Trigger Satellite Pass"):
    if st.session_state.simulation_run:
        # Add an extra satellite window
        new_window = (20, 25)
        if new_window not in st.session_state.satellite_windows:
            st.session_state.satellite_windows.append(new_window)
            st.sidebar.warning(f"Added satellite window: {new_window}")
            st.sidebar.info("Click 'Run Simulation' to apply changes")

if st.sidebar.button("🔧 Fuel Truck Failure"):
    if st.session_state.simulation_run:
        st.session_state.fuel_truck_capacity = 1
        st.sidebar.error("Fuel truck capacity reduced to 1!")
        st.sidebar.info("Click 'Run Simulation' to apply changes")

if st.sidebar.button("📈 Increase Traffic"):
    if st.session_state.simulation_run:
        st.session_state.num_aircraft += 3
        st.sidebar.success(f"Added 3 aircraft! Total: {st.session_state.num_aircraft}")
        st.sidebar.info("Click 'Run Simulation' to apply changes")

if st.sidebar.button("🔄 Reset Simulation"):
    st.session_state.simulation_run = False
    st.session_state.sim = None
    st.session_state.env = None
    st.session_state.num_aircraft = 3
    st.session_state.fuel_truck_capacity = 2
    st.session_state.satellite_windows = [(10, 15), (40, 45)]
    st.session_state.aircraft_counter = 3
    st.rerun()

# Display simulation results if run
if st.session_state.simulation_run and st.session_state.sim:
    sim = st.session_state.sim
    env = st.session_state.env
    
    # Satellite Status Indicator
    st.header("🛰️ Satellite Status")
    
    # Check if satellite was overhead during simulation
    satellite_active = any(event['event'] == 'satellite_delay' for event in sim.events)
    
    if satellite_active:
        st.warning(f"⚠️ Satellite passes detected during simulation at windows: {SATELLITE_WINDOWS}")
    else:
        st.success("✅ No satellite interference during operations")
    
    # Display satellite windows
    st.info(f"**Configured Satellite Windows:** {sim.satellite_windows}")
    
    st.divider()
    
    # Aircraft Status Table
    st.header("✈️ Aircraft Status")
    
    if sim.aircraft_states:
        # Create DataFrame from aircraft states
        aircraft_data = []
        for aircraft_name, state in sim.aircraft_states.items():
            aircraft_data.append({
                "Aircraft": aircraft_name,
                "Status": state['status'],
                "Current Operation": state['current_operation'],
                "Time in State": state['start_time']
            })
        
        df_aircraft = pd.DataFrame(aircraft_data)
        st.dataframe(df_aircraft, use_container_width=True, hide_index=True)
    else:
        st.info("No aircraft data available. Run simulation to see aircraft status.")
    
    st.divider()
    
    # Resource Status Panel
    st.header("🔧 Resource Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Runway",
            value=f"{sim.resource_states['runway']['in_use']}/{sim.resource_states['runway']['capacity']}",
            delta="Available" if sim.resource_states['runway']['in_use'] == 0 else "In Use"
        )
    
    with col2:
        st.metric(
            label="Fuel Trucks",
            value=f"{sim.resource_states['fuel_truck']['in_use']}/{sim.resource_states['fuel_truck']['capacity']}",
            delta="Available" if sim.resource_states['fuel_truck']['in_use'] < sim.resource_states['fuel_truck']['capacity'] else "Full"
        )
    
    with col3:
        st.metric(
            label="Weapon Teams",
            value=f"{sim.resource_states['weapon_team']['in_use']}/{sim.resource_states['weapon_team']['capacity']}",
            delta="Available" if sim.resource_states['weapon_team']['in_use'] == 0 else "In Use"
        )
    
    st.divider()
    
    # Simulation Event Timeline
    st.header("📋 Simulation Event Timeline")
    
    if sim.events:
        # Create DataFrame from events
        df_events = pd.DataFrame(sim.events)
        
        # Format the display
        st.dataframe(
            df_events,
            use_container_width=True,
            hide_index=True,
            column_config={
                "time": st.column_config.NumberColumn("Time", format="%.1f"),
                "aircraft": "Aircraft",
                "event": "Event",
                "status": "Status"
            }
        )
        
        # Summary statistics
        st.subheader("📊 Summary Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Events", len(sim.events))
        
        with col2:
            satellite_delays = len([e for e in sim.events if e['event'] == 'satellite_delay'])
            st.metric("Satellite Delays", satellite_delays)
        
        with col3:
            total_time = env.now
            st.metric("Total Simulation Time", f"{total_time:.1f} units")
    else:
        st.info("No events logged. Run simulation to see event timeline.")

else:
    # Welcome screen
    st.info("👈 Click **Run Simulation** in the sidebar to start the airbase digital twin simulation.")
    
    st.markdown("""
    ### About This Digital Twin
    
    This system simulates aircraft operations at an airbase, including:
    
    - **Aircraft Operations**: Landing → Refueling → Rearming → Takeoff
    - **Resource Management**: Runway, fuel trucks, and weapon teams
    - **Satellite Risk Awareness**: Operations pause during satellite detection windows
    - **Event Tracking**: Complete timeline of all operations
    
    ### How to Use
    
    1. Click **Run Simulation** to execute the simulation
    2. View real-time aircraft status and resource utilization
    3. Analyze the event timeline to understand operations
    4. Check satellite interference impact on operations
    """)
