import matplotlib.pyplot as plt

# Create a basic plot
plt.figure(figsize=(8, 5))

# Generate some data for the plot
x = range(1, 11)
y = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

# Plot the data
plt.plot(x, y, marker='o', linestyle='-', color='b', label='Prime numbers')

# Display current axis limits
current_xlim = plt.xlim()
current_ylim = plt.ylim()
print(f"Current X-axis limits: {current_xlim}")
print(f"Current Y-axis limits: {current_ylim}")

# Set new axis limits
new_xlim = (0, 12)
new_ylim = (0, 30)
plt.xlim(new_xlim)
plt.ylim(new_ylim)
print(f"New X-axis limits set to: {new_xlim}")
print(f"New Y-axis limits set to: {new_ylim}")

# Show plot with new limits
plt.title('Prime Numbers Graph with New Axis Limits')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.legend()
plt.grid(True)

# Display the plot
plt.show()
