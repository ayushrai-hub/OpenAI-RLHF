import matplotlib.pyplot as plt
import numpy as np

# Global dictionary to store coordinates
coordinates = {}

# Function to clear the coordinates dictionary
def clear_coordinates():
    global coordinates
    coordinates = {}

# Onclick function to handle events and update the coordinates dictionary
def onclick(event, ax, scatter):
    if event.inaxes:
        x, y = int(event.xdata), int(event.ydata)
        coordinates[(x, y)] = (x, y)
        print(f"Coordinates: x={x}, y={y}")
        print(f"Updated dictionary: {coordinates}")

# Function to create the plot and return the figure, axis, and scatter object
def create_plot(data):
    fig, ax = plt.subplots()
    cax = ax.imshow(data, cmap='viridis')
    
    # Connect onclick event to the handler function
    scatter = ax.scatter([], [], color='red')
    fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, ax, scatter))
    
    return fig, ax, scatter

# Data for the plot (2D numpy array)
data = np.random.rand(10, 10)

# Display the plot
fig, ax, scatter = create_plot(data)
plt.show()
