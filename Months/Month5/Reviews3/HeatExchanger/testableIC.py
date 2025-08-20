def calculate_total_surface_area(Q, U, LMTD):
    """
    Calculate the total surface area required for the heat exchanger.
    
    Parameters:
    Q (float): Heat transfer rate (W)
    U (float): Overall heat transfer coefficient (W/m²-K)
    LMTD (float): Log mean temperature difference (K)
    
    Returns:
    float: Total surface area (m²)
    """
    A = Q / (U * LMTD)
    return A

def calculate_channel_length(A, W, N):
    """
    Calculate the length for each channel of the heat exchanger.
    
    Parameters:
    A (float): Total surface area (m²)
    W (float): Width of one channel (m)
    N (int): Number of channels
    
    Returns:
    float: Length of each channel (m)
    """
    L = A / (W * N)
    return L

def calculate_cross_section_dimensions(Q, U, LMTD, W, N):
    """
    Calculate the rectangular cross section dimensions (length and surface area).
    
    Parameters:
    Q (float): Heat transfer rate (W)
    U (float): Overall heat transfer coefficient (W/m²-K)
    LMTD (float): Log mean temperature difference (K)
    W (float): Width of one channel (m)
    N (int): Number of channels
    
    Returns:
    tuple: Total surface area (m²) and length of each channel (m)
    """
    A = calculate_total_surface_area(Q, U, LMTD)
    L = calculate_channel_length(A, W, N)
    return A, L
