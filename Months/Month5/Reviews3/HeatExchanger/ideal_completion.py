# ideal_completion.py

def calculate_cross_section_dimensions(flow_rate, fluid_velocity, fixed_dimension=None, is_width=True):
 
    # Calculate the necessary cross-sectional area
    cross_section_area = flow_rate / fluid_velocity
    
    # Calculate dimensions 
    if fixed_dimension:
        if is_width:
            width = fixed_dimension
            height = cross_section_area / width
        else:
            height = fixed_dimension
            width = cross_section_area / height
    else:
        
        width = height = cross_section_area**0.5  # square root to find equal dimensions

    return (width, height)