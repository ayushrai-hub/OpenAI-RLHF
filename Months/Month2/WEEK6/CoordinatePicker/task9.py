import matplotlib.pyplot as plt
import numpy as np

# Initialize a dictionary to store the coordinates
coordinates = {}

def onclick(event):
    if event.inaxes:
        x, y = int(round(event.xdata)), int(round(event.ydata))
        coordinates[(x, y)] = (x, y)
        print(f"Picked: x={x}, y={y}")
        print(f"Current coordinates: {coordinates}")
        
        # Update the plot with picked points
        ax.plot(x, y, 'ro', markersize=5)
        fig.canvas.draw()

# Create sample data (replace with your actual data)
data = np.random.rand(10, 10)

# Set up the plot
fig, ax = plt.subplots()
ax.imshow(data, cmap='viridis')
ax.set_title("Click to pick coordinates")

# Connect the onclick event
fig.canvas.mpl_connect('button_press_event', onclick)

plt.show()

print("Final picked coordinates:", coordinates)