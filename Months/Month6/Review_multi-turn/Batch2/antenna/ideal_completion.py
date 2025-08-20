import math
cos = math.cos
sin = math.sin
pi = math.pi

def compute_complex_number(frequency_hz, theta_deg, d_meters=0.23):
    # Validate frequency
    if frequency_hz <= 0:
        raise ValueError("Frequency must be positive")
    # Speed of light
    c = 3e8
    # Convert angle to radians
    theta_rad = theta_deg * pi / 180.0
    # Compute phase shift
    phi = 2 * pi * frequency_hz * (d_meters * sin(theta_rad)) / c
    # Compute fixed-point representation
    real = int(round(cos(phi) * 32767)) & 0xFFFF
    imag = int(round(sin(phi) * 32767)) & 0xFFFF
    # Pack into 32-bit number: real high 16, imag low 16
    return (real << 16) | imag

def main():
    try:
        frequency_input = float(input("Enter frequency in Hz: "))
        angle_input = float(input("Enter angle in degrees: "))
    except Exception:
        return
    value = compute_complex_number(frequency_input, angle_input)
    print(hex(value))
