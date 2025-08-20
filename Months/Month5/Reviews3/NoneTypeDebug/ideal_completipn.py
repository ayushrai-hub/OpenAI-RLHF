# ideal_completion.py

import numpy as np

def compute_average_and_error(data, d_data):
    if len(data) != len(d_data):
        raise ValueError("Data and uncertainty arrays must have the same length.")
    if len(data) == 0:
        raise ValueError("Data array cannot be empty.")
    return np.mean(data), np.sqrt(np.sum(d_data**2)) / len(data)

def compute_cylinder_volume(length, diam):
    if length <= 0 or diam <= 0:
        raise ValueError("Length and diameter must be positive.")
    return np.pi * (diam / 2)**2 * length

def compute_rectangular_volume(length, base, depth):
    if length <= 0 or base <= 0 or depth <= 0:
        raise ValueError("Length, base, and depth must be positive.")
    return length * base * depth

def calculate_sphere_with_hole_volume(diam_sphere, diam_hole):
    if diam_sphere <= 0 or diam_hole <= 0:
        raise ValueError("Sphere diameter and hole diameter must be positive.")
    if diam_hole >= diam_sphere:
        raise ValueError("Hole diameter must be smaller than sphere diameter.")
    sphere_volume = 4/3 * np.pi * (diam_sphere / 2)**3
    hole_volume = 4/3 * np.pi * (diam_hole / 2)**3
    return sphere_volume - hole_volume

def compute_density(mass, volume, d_mass, d_volume):
    if mass <= 0 or volume <= 0:
        raise ValueError("Mass and volume must be positive.")
    density = mass / volume
    d_density = density * np.sqrt((d_mass / mass)**2 + (d_volume / volume)**2)
    return density, d_density

def process_material(lengthData, dLength, diamData, dDiam, massData, dMass, form="cylinder", baseData=None, dBase=None, depthData=None, dDepth=None, diamHoleData=None, dDiamHole=None):
    if form not in ["cylinder", "rectangle", "sphere_with_hole"]:
        raise ValueError("Form must be one of: 'cylinder', 'rectangle', or 'sphere_with_hole'.")
    
    try:
        avg_mass, d_avg_mass = compute_average_and_error(massData, dMass)
    except ValueError as e:
        raise ValueError(f"Mass data error: {e}")

    if form == "cylinder":
        try:
            avg_length, d_avg_length = compute_average_and_error(lengthData, dLength)
            avg_diam, d_avg_diam = compute_average_and_error(diamData, dDiam)
            total_volume = compute_cylinder_volume(avg_length, avg_diam)
            d_total_volume = total_volume * np.sqrt((d_avg_length / avg_length)**2 + (d_avg_diam / avg_diam)**2)
        except ValueError as e:
            raise ValueError(f"Cylinder data error: {e}")

    elif form == "rectangle":
        if baseData is None or dBase is None or depthData is None or dDepth is None:
            raise ValueError("Base and depth data must be provided for rectangular form.")
        try:
            avg_length, d_avg_length = compute_average_and_error(lengthData, dLength)
            avg_base, d_avg_base = compute_average_and_error(baseData, dBase)
            avg_depth, d_avg_depth = compute_average_and_error(depthData, dDepth)
            total_volume = compute_rectangular_volume(avg_length, avg_base, avg_depth)
            d_total_volume = total_volume * np.sqrt((d_avg_length / avg_length)**2 + (d_avg_base / avg_base)**2 + (d_avg_depth / avg_depth)**2)
        except ValueError as e:
            raise ValueError(f"Rectangular data error: {e}")

    elif form == "sphere_with_hole":
        if diamHoleData is None or dDiamHole is None:
            raise ValueError("Hole diameter data must be provided for 'sphere_with_hole' form.")
        try:
            avg_diameter_sphere, d_avg_diameter_sphere = compute_average_and_error(diamData, dDiam)
            avg_diameter_hole, d_avg_diameter_hole = compute_average_and_error(diamHoleData, dDiamHole)
            total_volume = calculate_sphere_with_hole_volume(avg_diameter_sphere, avg_diameter_hole)
            d_total_volume = total_volume * np.sqrt((d_avg_diameter_sphere / avg_diameter_sphere)**2 + (d_avg_diameter_hole / avg_diameter_hole)**2)
        except ValueError as e:
            raise ValueError(f"Sphere with hole data error: {e}")

    try:
        avg_density, d_avg_density = compute_density(avg_mass, total_volume, d_avg_mass, d_total_volume)
    except ValueError as e:
        raise ValueError(f"Density calculation error: {e}")

    print(f"Avg Mass: {avg_mass:.2f} g | Unc: {d_avg_mass:.2f} g")
    print(f"Volume: {total_volume:.2f} cm^3 | Unc: {d_total_volume:.2f} cm^3")
    print(f"Density: {avg_density:.2f} g/cm^3 | Unc: {d_avg_density:.2f} g/cm^3\n")