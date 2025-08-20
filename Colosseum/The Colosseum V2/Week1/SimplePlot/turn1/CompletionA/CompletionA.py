import matplotlib.pyplot as plt

# Create a simple plot
x = [0, 1, 2, 3, 4, 5]
y = [0, 2, 4, 8, 16, 32]

plt.plot(x, y)

# Display the current axis limits
current_xlim = plt.xlim()
current_ylim = plt.ylim()
print(f"Current x-axis limits: {current_xlim}")
print(f"Current y-axis limits: {current_ylim}")

# Set new axis limits
plt.xlim(1, 4)
plt.ylim(5, 30)

# Display updated axis limits
new_xlim = plt.xlim()
new_ylim = plt.ylim()
print(f"New x-axis limits: {new_xlim}")
print(f"New y-axis limits: {new_ylim}")

# Display the plot
plt.show()
