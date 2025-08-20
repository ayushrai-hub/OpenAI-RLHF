import matplotlib.pyplot as plt

# Required global variables
x2 = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

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
y_labels_1 = [f'{val}.0$\\times$10$^{{-10}}$' for val in y_ticks_1]

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
y_labels_2 = [f'{val}.0$\\times$10$^{{-10}}$' for val in y_ticks_2]

temperature_labels = ["(40°C)", "(60°C)", "(120°C)", "(140°C)", "(100°C)", "(80°C)", "(160°C)"]
markers = ['s', 'o', '<', '>', 'v', '^', 'D']

def create_voltage_current_plot(dataset_num: int, x2: list, currents: list, y_ticks: list, y_labels: list) -> plt.Figure:
    fig, ax = plt.subplots()
    
    for i in range(7):
        ax.plot(x2, currents[i], marker=markers[i], markersize=5, linestyle='-', label=temperature_labels[i])
    
    ax.set_xlabel('Energy (V)')
    ax.set_ylabel('Charge (A)')
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.legend(fontsize='small')
    
    return fig

def verify_datasets():
    datasets = [(currents_1, y_ticks_1, y_labels_1), (currents_2, y_ticks_2, y_labels_2)]
    
    for currents, y_ticks, y_labels in datasets:
        assert len(currents) == 7, "Each dataset must contain exactly 7 temperature curves"
        for curve in currents:
            assert len(curve) == 10, "Each temperature curve must contain exactly 10 data points"
            assert all(isinstance(value, (int, float)) and value >= 0 for value in curve), "All current values must be non-negative numbers"
        assert len(y_ticks) == len(y_labels), "Y-ticks and y-labels must match in length"
    
    print("All datasets verified successfully!")
