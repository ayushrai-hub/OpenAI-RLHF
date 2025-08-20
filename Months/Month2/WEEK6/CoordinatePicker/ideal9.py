import matplotlib.pyplot as plt
import numpy as np

class CoordinatePicker:
    def __init__(self):
        self.coordinates = {}
        self.fig, self.ax = plt.subplots()
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)

    def onclick(self, event):
        if event.inaxes:
            x, y = int(round(event.xdata)), int(round(event.ydata))
            self.coordinates[(x, y)] = (x, y)
            print(f"Coordinates: x={x}, y={y}")

    def plot_and_pick(self, data):
        self.ax.imshow(data, cmap='viridis')
        plt.show()
        return self.coordinates

# Example usage
if __name__ == "__main__":
    data = np.random.rand(10, 10)
    picker = CoordinatePicker()
    result = picker.plot_and_pick(data)
    print("Final coordinates:", result)