
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Tuple

# Global variable to store the coordinates
coordinates: Dict[Tuple[float, float], Tuple[float, float]] = {}

# Data for the plot
data = np.random.rand(10, 10)

def onclick(event) -> None:
    # Check if the click is within the axes (not in the toolbar or outside the plot)
    if event.inaxes:
        x, y = event.xdata, event.ydata
        coordinates[(x, y)] = (x, y)
        print(f"Coordinates: x={x}, y={y}")
        print(f"Updated dictionary: {coordinates}")

def create_plot() -> Tuple[plt.Figure, plt.Axes]:
    # Create a plot using imshow
    fig, ax = plt.subplots()
    ax.imshow(data, cmap='viridis')
    
    # Connect the onclick event to the function
    fig.canvas.mpl_connect('button_press_event', onclick)
    
    return fig, ax

# Example usage to display the plot
fig, ax = create_plot()
plt.show()