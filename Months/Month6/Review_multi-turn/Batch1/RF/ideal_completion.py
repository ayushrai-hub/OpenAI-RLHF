import math

def compute_complex_number(frequency_hz, theta_deg, d_meters=0.23):
    if frequency_hz <= 0:
        raise ValueError("Frequency must be a positive non-zero value.")
    c = 299792458  # Speed of light in meters per second
    wavelength = c / frequency_hz  # Wavelength in meters
    theta_rad = math.radians(theta_deg)  # Convert angle to radians
    phase_difference = (2 * math.pi * d_meters * math.sin(theta_rad)) / wavelength  # Phase difference
    real_part = math.cos(phase_difference)  # Real part of the complex number
    imag_part = math.sin(phase_difference)  # Imaginary part of the complex number
    real_fixed = int(real_part * 32767)  # Convert to 16-bit signed integer
    imag_fixed = int(imag_part * 32767)  # Convert to 16-bit signed integer
    complex_number = (real_fixed << 16) | (imag_fixed & 0xFFFF)  # Combine into a 32-bit integer
    return complex_number

def main():
    frequency_hz = float(input("Enter the frequency in Hz: "))
    theta_deg = float(input("Enter the angle in degrees: "))
    result = compute_complex_number(frequency_hz, theta_deg)
    print(f"Complex number (hex): {result:08X}")

if __name__ == "__main__":
    main()