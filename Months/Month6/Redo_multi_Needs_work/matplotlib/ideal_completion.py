# ideal_completion.py
import matplotlib.pyplot as plt

def create_voltage_current_plot(dataset_num, x2, currents, y_ticks, y_labels):
    """
    Create a voltage vs current plot with fixed formatting
    
    Args:
        dataset_num: Dataset number for identification
        x2: List of voltage values
        currents: List of 7 lists, each containing 10 current measurements
        y_ticks: List of y-axis tick positions
        y_labels: List of y-axis tick labels
        
    Returns:
        matplotlib.figure.Figure: The created plot
    """
    plt.figure(figsize=(10, 6))
    
    # Temperature labels
    temp_labels = [
        "(40°C)", "(60°C)", "(120°C)", "(140°C)",
        "(100°C)", "(80°C)", "(160°C)"
    ]
    
    # Required markers in specific order
    markers = ['s', 'o', '<', '>', 'v', '^', 'D']
    
    # Verify input data structure
    if len(currents) != 7:
        raise ValueError(f"Dataset {dataset_num} must have exactly 7 temperature curves")
    if any(len(curve) != 10 for curve in currents):
        raise ValueError(f"Dataset {dataset_num} must have exactly 10 points per curve")
    
    # Plot data with specified markers
    for curr, temp, marker in zip(currents, temp_labels, markers):
        plt.plot(x2, curr, marker=marker, markersize=5, linestyle='-', label=temp)

    plt.xlabel('Energy(V)')
    plt.ylabel('Charge(A)')
    plt.xticks(rotation=0, fontsize=10)
    
    # Ensure y_labels matches y_ticks in length
    if len(y_ticks) != len(y_labels):
        raise ValueError(f"Dataset {dataset_num}: y_ticks and y_labels must have same length")
    plt.yticks(y_ticks, y_labels)
    
    # Add legend
    plt.legend(fontsize='small')
    plt.tight_layout()
    return plt.gcf()

def verify_datasets(datasets):
    """
    Verify that all datasets meet structural requirements
    
    Args:
        datasets: List of tuples (currents, y_ticks, y_labels)
    """

    try:
        for i, (currents, y_ticks, y_labels) in enumerate(datasets, 1):
        # Check dataset structure
            if len(currents) != 7:
                raise ValueError(f"Dataset {i}: Must have exactly 7 temperature curves")
            if any(len(curve) != 10 for curve in currents):
                raise ValueError(f"Dataset {i}: Each curve must have exactly 10 points")
                
                # Check ticks and labels alignment
            if len(y_ticks) != len(y_labels):
                raise False
        return True
    except Exception:
        return False

# Common x-axis values
x2 = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# Dataset 1
currents_1 = [
    [2, 2.15, 2.6, 3, 3.2, 3.4, 4, 4.25, 4.5, 4.75],
    [3, 3.25, 3.3, 3.5, 3.5, 3.7, 4.5, 5.1, 5.6, 6],
    [4, 3.5, 4.3, 4.8, 5.4, 4.8, 5.3, 5.8, 6.1, 6.6],
    [3.5, 3.56, 4.5, 5.6, 5.9, 6, 6.5, 7, 7.6, 8.3],
    [3.1, 3.8, 5.3, 5.8, 6.4, 7.2, 8.9, 8.9, 10.2, 12],
    [5, 4.5, 6.2, 6.3, 8.2, 10.5, 11.7, 12.6, 15.3, 15.2],
    [6, 6.6, 7.5, 8.4, 9.5, 12.4, 14, 15.5, 17, 20]
]
y_ticks_1 = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
y_labels_1 = [
    '5.0×10⁻¹⁰', '1.0×10⁻¹⁰', '1.5×10⁻¹⁰', '2.0×10⁻¹⁰',
    '5.0×10⁻¹⁰', '6.0×10⁻¹⁰', '7.0×10⁻¹⁰', '8.0×10⁻¹⁰',
    '9.0×10⁻¹⁰', '10×10⁻¹⁰'
]

# Dataset 2
currents_2 = [
    [0.6, 1.2, 1.3, 1.5, 1.5, 1.8, 1.7, 1.8, 2.2, 1.9],
    [1.2, 1.3, 1.4, 1.8, 1.8, 1.8, 2.2, 2.3, 2.5, 2.9],
    [1.2, 1.2, 1.4, 1.7, 2, 2.5, 2.7, 3, 2.9, 3.5],
    [1, 1.7, 1.9, 2.5, 2.8, 1.8, 2.3, 3.5, 3.5, 3.7],
    [1.2, 1.7, 2, 2.5, 2.8, 3.5, 3.5, 3.6, 4, 5],
    [1.3, 2, 3.2, 2.8, 3.7, 3.9, 4.5, 5.3, 6, 6.5],
    [2, 3, 9, 2.8, 3.5, 3, 6.4, 7, 7.7, 9.2]
]
y_ticks_2 = [1, 2, 3, 4, 6, 7]
y_labels_2 = [
    '2.0×10⁻¹⁰', '4.0×10⁻¹⁰', '6.0×10⁻¹⁰',
    '8.0×10⁻¹⁰', '1.0×10⁻¹⁰', '1.2×10⁻¹⁰'
]

# Dataset 3
currents_3 = [
    [0.3, 0.7, 0.7, 0.8, 0.9, 1.2, 1.3, 1.2, 1.8, 1.7],
    [0.5, 0.6, 0.6, 0.8, 0.9, 1.2, 1.2, 1.8, 1.9, 1.9],
    [0.5, 0.7, 0.8, 1, 1.1, 1.5, 1.4, 1.5, 1.8, 2.2],
    [0.7, 0.8, 1, 0.9, 1.3, 1.4, 1.5, 1.8, 2, 2.3],
    [0.6, 1, 0.9, 1.1, 1.5, 1.8, 2.1, 2, 2.5, 3],
    [0.8, 1, 1.3, 1.4, 1.8, 2, 2.5, 3.2, 3.3, 4],
    [0.8, 1.2, 1.7, 2, 2.3, 3, 3.3, 3.8, 4.2, 4.8]
]
y_ticks_3 = [1, 2, 3, 4, 5]
y_labels_3 = [
    '2.0×10⁻¹⁰', '4.0×10⁻¹⁰', '6.0×10⁻¹⁰',
    '8.0×10⁻¹⁰', '1.0×10⁻¹⁰'
]

# Dataset 4
currents_4 = [
    [0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.6, 2.1, 2.3, 2.5],
    [0.4, 0.6, 1.1, 1.5, 1.3, 1.8, 1.9, 2.4, 2.6, 2.9],
    [0.6, 0.9, 1.1, 1.5, 1.7, 2, 2.1, 2.6, 2.9, 3.1],
    [0.8, 1, 1.2, 1.4, 1.8, 2, 2.6, 3, 3.5, 3.8],
    [0.9, 1.1, 1.5, 1.9, 2.1, 2.3, 2.8, 3.2, 3.7, 4.3],
    [0.8, 1.2, 1.5, 2, 2.3, 2.8, 3, 3.5, 4, 4.4],
    [0.9, 1.2, 1.8, 2.5, 2.9, 3.7, 4.5, 5.2, 6, 6.5]
]
y_ticks_4 = [1, 2, 3, 4, 5, 6, 7, 8]
y_labels_4 = [
    '5.0×10⁻¹⁰', '1.0×10⁻¹⁰', '1.5×10⁻¹⁰', '2.0×10⁻¹⁰',
    '2.5×10⁻¹⁰', '3.0×10⁻¹⁰', '3.5×10⁻¹⁰', '4.0×10⁻¹⁰'
]
# Generate all plots with verification
datasets = [
    (currents_1, y_ticks_1, y_labels_1),
    (currents_2, y_ticks_2, y_labels_2),
    (currents_3, y_ticks_3, y_labels_3),
    (currents_4, y_ticks_4, y_labels_4)
]

# Verify and create plots
verify_datasets(datasets)
for i, (currents, y_ticks, y_labels) in enumerate(datasets, 1):
    fig = create_voltage_current_plot(i, x2, currents, y_ticks, y_labels)
    plt.close()