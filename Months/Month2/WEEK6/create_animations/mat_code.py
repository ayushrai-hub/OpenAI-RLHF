import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

def create_animations(num_animations=3):
    # Create a figure with the required number of subplots
    fig, axs = plt.subplots(1, num_animations, figsize=(5 * num_animations, 5))
    
    # Ensure axs is iterable, even for a single subplot
    if num_animations == 1:
        axs = [axs]

    # Store the lines and animations
    lines = []
    animations = []

    # Generate data and functions for each animation
    for i in range(num_animations):
        x = np.linspace(0, 2 * np.pi, 128)
        y = np.sin(x) * np.cos((i + 1) * x)  # Different initial data for variety
        line, = axs[i].plot(x, y, color=np.random.rand(3,))  # Random color for each line
        lines.append(line)

        # Update function for this subplot
        def update(frame, line=line, x=x, i=i):
            y = np.sin(x + frame / 10.0 + i) * np.cos(x + frame / 15.0 + i)
            line.set_ydata(y)
            return line,

        # Create an animation for this subplot
        ani = FuncAnimation(fig, update, frames=200, blit=True, interval=50)
        animations.append(ani)

    # Display the animations
    plt.show()

# Example usage
create_animations(num_animations=5)
