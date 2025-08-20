import matplotlib.pyplot as plt

# Create a simple plot
x = [0, 1, 2, 3, 4, 5]
y = [0, 2, 4, 6, 8, 10]
plt.plot(x, y)

# Display current axis limits
current_xlim = plt.gca().get_xlim()
current_ylim = plt.gca().get_ylim()
print("Current X-axis limits:", current_xlim)
print("Current Y-axis limits:", current_ylim)

# Set new axis limits
plt.xlim(1, 4)
plt.ylim(1, 8)

# Display the updated limits
print("Updated X-axis limits:", plt.gca().get_xlim())
print("Updated Y-axis limits:", plt.gca().get_ylim())

plt.title('Plot with Updated Axis Limits')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.grid(True)
plt.show()
