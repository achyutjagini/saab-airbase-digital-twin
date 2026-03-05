# Scheduler Module

def schedule_aircraft(aircraft_list, satellite_windows=None):
    """
    Simple priority-based scheduler for aircraft operations.
    
    Args:
        aircraft_list: List of Aircraft objects
        satellite_windows: List of (start, end) tuples for satellite passes
    
    Returns:
        Sorted list of aircraft by priority (high to low)
    """
    # Sort aircraft by priority (higher priority first)
    # Secondary sort by name for consistency
    scheduled = sorted(
        aircraft_list,
        key=lambda a: (-a.priority, a.name)
    )
    
    return scheduled


def predict_delays(aircraft_list, satellite_windows=None):
    """
    Predict potential delays for aircraft based on resource contention
    and satellite windows.
    
    Args:
        aircraft_list: List of Aircraft objects
        satellite_windows: List of (start, end) tuples for satellite passes
    
    Returns:
        Dictionary mapping aircraft names to predicted delay info
    """
    if satellite_windows is None:
        satellite_windows = []
    
    delays = {}
    
    # Simple heuristic: estimate delays based on queue position
    # Assume each aircraft takes ~23 time units (3+8+10+2)
    base_time_per_aircraft = 23
    
    for idx, aircraft in enumerate(aircraft_list):
        estimated_start = idx * base_time_per_aircraft
        estimated_end = estimated_start + base_time_per_aircraft
        
        # Check for satellite interference
        satellite_delay = 0
        for sat_start, sat_end in satellite_windows:
            # If aircraft operations overlap with satellite window
            if estimated_start < sat_end and estimated_end > sat_start:
                # Estimate delay as the overlap duration
                overlap_start = max(estimated_start, sat_start)
                overlap_end = min(estimated_end, sat_end)
                satellite_delay += (overlap_end - overlap_start)
        
        # Resource contention delay (simple queue-based estimate)
        # Aircraft waiting behind others in queue
        queue_delay = idx * 2  # Simple heuristic
        
        total_delay = satellite_delay + queue_delay
        
        delays[aircraft.name] = {
            "satellite_delay": satellite_delay,
            "queue_delay": queue_delay,
            "total_delay": total_delay,
            "reason": []
        }
        
        # Add reasons for delays
        if queue_delay > 0:
            delays[aircraft.name]["reason"].append(f"runway queue (+{queue_delay} min)")
        if satellite_delay > 0:
            delays[aircraft.name]["reason"].append(f"satellite window (+{satellite_delay} min)")
    
    return delays
