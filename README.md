# Digital Twin for AI Airbase Operations Planning
A simulation-based digital twin for airbase operations that models aircraft turnaround activities (landing, refueling, rearming, and takeoff) while accounting for operational constraints such as limited resources and satellite observation risk.

The system combines discrete-event simulation (SimPy) with an interactive dashboard (Streamlit) to visualize operations and predict delays in real time.

---

## 🚀 Project Overview

Modern airbases must manage complex operational workflows involving multiple aircraft, limited ground resources, and external constraints such as satellite surveillance.

This project implements a **Digital Twin of an Airbase**, enabling:

- Simulation of aircraft turnaround operations
- Resource allocation modeling (runways, fuel trucks, weapon crews)
- Satellite observation risk windows
- Delay prediction and operational planning
- Interactive scenario testing through a web dashboard

The system demonstrates how AI-assisted planning tools can help optimize airbase operations and minimize delays.

---

## 🧠 Key Features

### Aircraft Turnaround Simulation

Models the full operational workflow:

```
Landing → Refueling → Rearming → Takeoff
```

Each step consumes limited resources.

### Resource Constraints

The airbase includes limited operational resources:

- Runway capacity
- Fuel trucks
- Weapon crews

Aircraft must queue for resources, creating realistic operational delays.

### Satellite Observation Risk

Operations such as refueling or rearming are delayed when satellites are overhead.

Example satellite windows: `[10, 15]` `[40, 45]`

This simulates operational security constraints.

### Intelligent Scheduling

A priority-based scheduler assigns aircraft operations to reduce conflicts and minimize delay risk.

### Interactive Dashboard

A Streamlit dashboard allows users to:

- Configure simulation scenarios
- Adjust number of aircraft
- Modify resource capacity
- Trigger satellite passes
- Visualize operational timelines
- Predict delays

---

## 🖥 Dashboard Preview

The dashboard provides:

- Aircraft status tracking
- Simulation event timeline
- Satellite risk alerts
- Predicted operational delays
- Scenario controls

---

## 🏗 System Architecture

```
Aircraft Model
      ↓
Priority Scheduler
      ↓
SimPy Discrete Event Simulation
      ↓
Event Logging System
      ↓
Streamlit Dashboard Visualization
```

---

## 📁 Project Structure

```
saab-airbase-digital-twin/
├── dashboard/
│   └── dashboard.py          # Streamlit UI
├── simulation/
│   └── simulator.py          # SimPy simulation engine
├── model/
│   └── airbase_model.py      # Aircraft and airbase models
├── optimizer/
│   └── scheduler.py          # Aircraft scheduling logic
├── main.py                   # CLI simulation entry point
├── requirements.txt          # Dependencies
└── README.md
```

---

## ⚙️ Installation

**Clone the repository:**

```bash
git clone https://github.com/your-repo/airbase-digital-twin.git
cd airbase-digital-twin
```

**Create a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Simulation

Run the command line simulation:

```bash
python main.py
```

**Example output:**

```
0:  Jet-1 requesting landing
3:  Jet-1 refueling
11: Satellite overhead, delaying rearm
26: Jet-1 taking off
28: Jet-1 departed
```

---

## 📊 Running the Dashboard

Start the interactive dashboard:

```bash
streamlit run dashboard/dashboard.py
```

Then open: [http://localhost:8501](http://localhost:8501)

---

## 🎮 Interactive Scenarios

Users can test operational scenarios such as:

- Increasing aircraft traffic
- Reducing fuel truck capacity
- Triggering satellite passes
- Adding new aircraft dynamically

This allows exploration of operational bottlenecks and delay impacts.

---

## 📈 Example Use Cases

The system can be used for:

- Airbase operations planning
- Training and simulation
- Logistics optimization
- Operational risk analysis
- Resource allocation experiments

---

## 🛠 Technologies Used

| Tool | Purpose |
|------|---------|
| Python | Core language |
| SimPy | Discrete event simulation |
| Streamlit | Interactive dashboards |
| Pandas | Data analysis |
| Altair | Visualization |


