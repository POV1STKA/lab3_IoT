from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData


def process_agent_data(agent_data: AgentData):
    """
    Process agent data and classify the state of the road surface.

    Parameters:
        agent_data (AgentData): Agent data containing accelerometer, GPS, and timestamp.

    Returns:
        processed_data (dict): Processed data containing the classified state of the road surface.
    """
    # Accessing the accelerometer data from the AgentData instance
    x_acceleration = agent_data.accelerometer.x
    y_acceleration = agent_data.accelerometer.y
    z_acceleration = agent_data.accelerometer.z

    # Calculate the magnitude of acceleration (you can use any formula based on your accelerometer data format)
    acceleration_magnitude = (
        x_acceleration**2 + y_acceleration**2 + z_acceleration**2
    ) ** 0.5

    # Classify the road surface based on the acceleration magnitude
    if acceleration_magnitude < 0.2:
        road_state = "normal"
    elif acceleration_magnitude >= 0.2 and acceleration_magnitude < 0.5:
        road_state = "traffic cop/curb"
    elif acceleration_magnitude >= 0.5 and acceleration_magnitude < 1.0:
        road_state = "small pits"
    else:
        road_state = "large pits"

    # Create a dictionary to store the classified road surface state
    processed_data = ProcessedAgentData(road_state=road_state)

    return processed_data
