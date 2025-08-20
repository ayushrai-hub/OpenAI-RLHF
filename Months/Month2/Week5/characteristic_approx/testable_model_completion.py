import numpy as np

def characteristic_approx(x, a, b):
    """
    Approximates the characteristic function of the interval [-a, a].

    Parameters:
    - x: array-like, input values
    - a: float, half-width of the interval
    - b: float, controls the steepness of the transition

    Returns:
    - Array-like approximation of the characteristic function.
    """
    return np.exp(-((x + a) / b)**2) * np.exp(-((x - a) / b)**2)

# Example usage (this should be removed when running unit tests)
if __name__ == "__main__":
    x = np.linspace(-4, 4, 400)
    y = characteristic_approx(x, 2, 0.5)

    import matplotlib.pyplot as plt
    plt.plot(x, y, label=r'$f(x)$')
    plt.axhline(0, color='r', linestyle='--', label='Step function (Low)')
    plt.axhline(1, color='r', linestyle='--', label='Step function (High)')
    plt.axvline(-2, color='g', linestyle='--', label='Interval boundary')
    plt.axvline(2, color='g', linestyle='--', label='Interval boundary')
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.title('Exponential Function Approximating the Characteristic Function of [-a, a]')
    plt.legend()
    plt.grid(True)
    plt.show()
