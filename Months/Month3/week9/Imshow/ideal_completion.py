#ideal_completion.py

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Tuple

# Create sample data for imshow
data = np.random.rand(10, 10)

# Initialize a dictionary to store the coordinates
coordinates: Dict[Tuple[int, int], float] = {}

def onclick(event, ax, scatter):
    global coordinates
    if event.inaxes != ax:
        return coordinates

    try:
        x = int(round(event.xdata))
        y = int(round(event.ydata))
    except (TypeError, ValueError):
        print("Invalid coordinate values")
        return coordinates

    if 0 <= x < data.shape[1] and 0 <= y < data.shape[0]:
        coordinates[(x, y)] = data[y, x]  # Store the data value at (x, y)
        print(f"Picked coordinate: x={x}, y={y}, value={data[y, x]:.4f}")

        # Update scatter plot
        scatter.set_offsets(np.array(list(coordinates.keys())))

        # Update text annotations
        for txt in ax.texts:
            txt.remove()
        for (x, y), value in coordinates.items():
            ax.text(x, y, f'{value:.2f}', ha='center', va='center', color='red', fontweight='bold')

        plt.draw()
    else:
        print(f"Coordinate ({x}, {y}) is out of bounds")

    return coordinates

def create_plot(data):
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(data, cmap='viridis', interpolation='nearest')
    plt.colorbar(im)

    # Initialize empty scatter plot for picked points
    scatter = ax.scatter([], [], color='red', s=100, marker='x')

    # Connect the onclick event to the function
    fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, ax, scatter))

    plt.title("Click on the image to pick coordinates")
    return fig, ax, scatter

def clear_coordinates():
    global coordinates
    coordinates.clear()

# Only create the plot if this script is run directly
if __name__ == "__main__":
    fig, ax, scatter = create_plot(data)
    plt.show()

    print("Final coordinates dictionary:")
    for coord, value in coordinates.items():
        print(f"Coordinate {coord}: value {value:.4f}")