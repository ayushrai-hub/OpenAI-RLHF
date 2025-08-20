import numpy as np
import matplotlib.pyplot as plt

# Parameters for the exponential function
a = 2    # Half-width of the interval
b = 0.5  # Controls the width of the transition

# Generate input values
x = np.linspace(-4, 4, 400)

# Compute the approximation of the step function
y = np.exp(-((x + a) / b)**2) * np.exp(-((x - a) / b)**2)

# Plot the approximation
plt.plot(x, y, label=r'$f(x) = \exp\left(-\left(\frac{x + a}{b}\right)^2\right) \cdot \exp\left(-\left(\frac{x - a}{b}\right)^2\right)$')
plt.axhline(0, color='r', linestyle='--', label='Step function (Low)')
plt.axhline(1, color='r', linestyle='--', label='Step function (High)')
plt.axvline(-a, color='g', linestyle='--', label='Interval boundary')
plt.axvline(a, color='g', linestyle='--', label='Interval boundary')
plt.xlabel('x')
plt.ylabel('f(x)')
plt.title('Exponential Function Approximating the Characteristic Function of [-a, a]')
plt.legend()
plt.grid(True)
plt.show()
