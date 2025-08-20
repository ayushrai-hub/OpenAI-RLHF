import numpy as np
import matplotlib.pyplot as plt

def characteristic_approx(x, a, b):
    """
    Approximate the characteristic function of [-a, a] using exponentials.
    
    Parameters:
    x : array-like, input values
    a : float, half-width of the interval
    b : float, controls the steepness of the transition
    
    Returns:
    array-like, approximation of the characteristic function
    """
    return 0.5 * (np.tanh((x + a) / b) - np.tanh((x - a) / b))
# Set up parameters
a = 2  # Half-width of the interval
b_values = [0.1, 0.5, 1.0]  # Different steepness values to compare
x = np.linspace(-4, 4, 400)

# Create the plot
plt.figure(figsize=(12, 6))

# Plot the true characteristic function
plt.step(x, np.abs(x) <= a, 'k--', label='True characteristic function', where='mid')

# Plot approximations for different b values
for b in b_values:
    y = characteristic_approx(x, a, b)
    plt.plot(x, y, label=f'Approximation (b={b})')

# Customize the plot
plt.xlabel('x')
plt.ylabel('f(x)')
plt.title(f'Exponential Approximation of Characteristic Function for [-{a}, {a}]')
plt.legend()
plt.grid(True)
plt.ylim(-0.1, 1.1)

# Add vertical lines to show the interval boundaries
plt.axvline(-a, color='r', linestyle=':', alpha=0.5)
plt.axvline(a, color='r', linestyle=':', alpha=0.5)

plt.show()



for b in b_values:
    y = characteristic_approx(x, a, b)
    print(f"For b={b}:")
    print(f"  Min value: {y.min():.4f}")
    print(f"  Max value: {y.max():.4f}")
    print(f"  Value at x=0: {characteristic_approx(0, a, b):.4f}")
    print(f"  Value at x=3: {characteristic_approx(3, a, b):.4f}")
    
    # Approximate integral
    integral = np.trapz(y, x)
    print(f"  Approximate integral: {integral:.4f}")
    print()
