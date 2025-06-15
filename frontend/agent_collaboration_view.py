# Import necessary libraries
import plotly as plt

# Define data structure
agents = []

# Function to update visualization with new data
def update_visualization():
    for agent in agents:
        # Update plot with new data
        plot.update_traces([agent])

# Start real-time communication with ChatDev server
websocket = pywebsocket.create_connection("ws://localhost:8000/chatdev/ws")

# Receive agent state updates
while True:
    state = websocket.recv()
    agents.append(state)
    update_visualization()

# Stop communication when the program exits
websocket.close()