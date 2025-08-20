import matplotlib.pyplot as plt


def main():
    # Initialize a dictionary to store the coordinates
    coordinates = {}

    def onclick(event):
        # Check if the click is within the axes (not in the toolbar or outside the plot)
        if event.inaxes:
            x, y = event.xdata, event.ydata
            coordinates[(event.xdata, event.ydata)] = (x, y)
            print(f"Coordinates: x={x}, y={y}")
            print(f"Updated dictionary: {coordinates}")

    # Create some data to display with imshow
    import numpy as np
    data = np.random.rand(10, 10)

    # Plot the data using imshow
    fig, ax = plt.subplots()
    cax = ax.imshow(data, cmap='viridis')

    # Connect the onclick event to the function
    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    plt.show()

    # After closing the plot, you can see the dictionary with all the coordinates picked
    print("Final coordinates:", coordinates)


if __name__ == '__main__':
    main()