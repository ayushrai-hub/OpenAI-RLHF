import matplotlib.pyplot as plt

# Create a simple plot
x = [1, 2, 3, 4, 5]
y = [1, 4, 9, 16, 25]
plt.plot(x, y)
plt.xlabel('X-axis')
plt.ylabel('Y-axis')

# Display current axis limits
print(f"Current x-limits: {plt.xlim()}")
print(f"Current y-limits: {plt.ylim()}")

# Set new axis limits
plt.xlim(0, 6)
plt.ylim(0, 30)

# Display the new axis limits
print(f"New x-limits: {plt.xlim()}")
print(f"New y-limits: {plt.ylim()}")

# Show the plot
plt.show()
