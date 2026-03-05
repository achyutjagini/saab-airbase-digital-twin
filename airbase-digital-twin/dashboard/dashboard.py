import sys
import os
import streamlit as st
import simpy
import pandas as pd
import altair as alt

# add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.simulator import AirbaseSimulation, satellite_overhead, SATELLITE_WINDOWS
from model.airbase_model import Aircraft
from optimizer.scheduler import schedule_aircraft, predict_delays


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
    st.session_state.predicted_delays = {}

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
    
    # Schedule aircraft using priority scheduler
    scheduled_aircraft = schedule_aircraft(aircraft_list, st.session_state.satellite_windows)
    
    # Predict delays
    predicted_delays = predict_delays(scheduled_aircraft, st.session_state.satellite_windows)
    
    # Start aircraft processes in scheduled order
    for aircraft in scheduled_aircraft:
        env.process(sim.aircraft_process(aircraft))
    
    # Run simulation
    env.run()
    
    # Store in session state
    st.session_state.simulation_run = True
    st.session_state.sim = sim
    st.session_state.env = env
    st.session_state.aircraft_counter = num_aircraft
    st.session_state.predicted_delays = predicted_delays
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
    st.session_state.predicted_delays = {}
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
        st.warning(f"⚠️ Satellite passes detected during simulation at windows: {sim.satellite_windows}")
    else:
        st.success("✅ No satellite interference during operations")
    
    # Display satellite windows
    st.info(f"**Configured Satellite Windows:** {sim.satellite_windows}")
    
    st.divider()
    
    # Predictive Delay Panel
    st.header("⚠️ Predicted Delays")
    
    if st.session_state.predicted_delays:
        delays = st.session_state.predicted_delays
        
        # Filter aircraft with delays
        delayed_aircraft = {k: v for k, v in delays.items() if v['total_delay'] > 0}
        
        if delayed_aircraft:
            st.warning("**AI-Predicted Operational Delays:**")
            
            for aircraft_name, delay_info in delayed_aircraft.items():
                reason_str = ", ".join(delay_info['reason']) if delay_info['reason'] else "resource contention"
                st.markdown(f"- **{aircraft_name}** → +{delay_info['total_delay']:.0f} min ({reason_str})")
        else:
            st.success("✅ No significant delays predicted for current configuration")
    
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
    
    st.divider()
    
    # Visualizations
    st.header("📊 Visualizations")
    
    if sim.events:
        # Aircraft Timeline (Gantt Chart)
        st.subheader("✈️ Aircraft Operations Timeline")
        
        # Prepare data for Gantt chart
        timeline_data = []
        aircraft_operations = {}
        
        for event in sim.events:
            aircraft = event['aircraft']
            if aircraft not in aircraft_operations:
                aircraft_operations[aircraft] = []
            
            # Track start and end of operations
            if event['status'] == 'in_progress':
                aircraft_operations[aircraft].append({
                    'operation': event['event'],
                    'start': event['time']
                })
            elif event['status'] == 'completed' and aircraft_operations[aircraft]:
                # Find matching start event
                for op in reversed(aircraft_operations[aircraft]):
                    if op['operation'] == event['event'] and 'end' not in op:
                        op['end'] = event['time']
                        timeline_data.append({
                            'Aircraft': aircraft,
                            'Operation': event['event'].replace('_', ' ').title(),
                            'Start': op['start'],
                            'End': event['time']
                        })
                        break
        
        if timeline_data:
            df_timeline = pd.DataFrame(timeline_data)
            
            # Create Gantt chart
            chart = alt.Chart(df_timeline).mark_bar().encode(
                x=alt.X('Start:Q', title='Time'),
                x2='End:Q',
                y=alt.Y('Aircraft:N', title='Aircraft'),
                color=alt.Color('Operation:N', title='Operation Type'),
                tooltip=['Aircraft', 'Operation', 'Start', 'End']
            ).properties(
                height=300,
                title='Aircraft Operations Timeline'
            )
            
            # Add satellite windows as background
            sat_windows_data = []
            for start, end in sim.satellite_windows:
                sat_windows_data.append({'start': start, 'end': end})
            
            if sat_windows_data:
                df_sat = pd.DataFrame(sat_windows_data)
                sat_overlay = alt.Chart(df_sat).mark_rect(opacity=0.2, color='red').encode(
                    x='start:Q',
                    x2='end:Q'
                )
                chart = sat_overlay + chart
            
            st.altair_chart(chart, use_container_width=True)
        
        st.divider()
        
        # Resource Utilization Chart
        st.subheader("🔧 Resource Utilization Over Time")
        
        # Prepare resource utilization data
        resource_timeline = []
        for event in sim.events:
            if event['event'] in ['landing', 'takeoff']:
                resource_timeline.append({
                    'Time': event['time'],
                    'Resource': 'Runway',
                    'Status': 'In Use' if event['status'] == 'in_progress' else 'Available'
                })
            elif event['event'] == 'refueling':
                resource_timeline.append({
                    'Time': event['time'],
                    'Resource': 'Fuel Truck',
                    'Status': 'In Use' if event['status'] == 'in_progress' else 'Available'
                })
            elif event['event'] == 'rearming':
                resource_timeline.append({
                    'Time': event['time'],
                    'Resource': 'Weapon Team',
                    'Status': 'In Use' if event['status'] == 'in_progress' else 'Available'
                })
        
        if resource_timeline:
            df_resources = pd.DataFrame(resource_timeline)
            
            # Count in-use resources over time
            resource_counts = df_resources.groupby(['Time', 'Resource', 'Status']).size().reset_index(name='Count')
            
            # Create line chart
            resource_chart = alt.Chart(resource_counts[resource_counts['Status'] == 'In Use']).mark_line(point=True).encode(
                x=alt.X('Time:Q', title='Simulation Time'),
                y=alt.Y('Count:Q', title='Resources In Use'),
                color=alt.Color('Resource:N', title='Resource Type'),
                tooltip=['Time', 'Resource', 'Count']
            ).properties(
                height=300,
                title='Resource Utilization Over Time'
            )
            
            st.altair_chart(resource_chart, use_container_width=True)

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
    - **AI-Powered Scheduling**: Priority-based aircraft scheduling
    - **Predictive Analytics**: Delay prediction and optimization
    
    ### How to Use
    
    1. Configure scenario parameters in the sidebar
    2. Click **Run Simulation** to execute the simulation
    3. View real-time aircraft status and resource utilization
    4. Analyze the event timeline and visualizations
    5. Test different scenarios using interactive controls
    6. Check satellite interference impact on operations
    """)
