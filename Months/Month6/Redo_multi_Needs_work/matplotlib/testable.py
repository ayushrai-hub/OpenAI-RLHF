import matplotlib.pyplot as plt

# Global Variables
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
y_labels_1 = [f"{val}.0×10⁻¹⁰" for val in y_ticks_1]

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
y_labels_2 = [f"{val}.0×10⁻¹⁰" for val in y_ticks_2]

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
y_labels_3 = [f"{val}.0×10⁻¹⁰" for val in y_ticks_3]

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
y_labels_4 = [f"{val}.0×10⁻¹⁰" for val in y_ticks_4]

def create_voltage_current_plot(dataset_num, x2, currents, y_ticks, y_labels):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    markers = ['s', 'o', '<', '>', 'v', '^', 'D']
    labels = ["(40°C)", "(60°C)", "(120°C)", "(140°C)", "(100°C)", "(80°C)", "(160°C)"]

    for i in range(7):
        ax.plot(x2, currents[i], marker=markers[i], markersize=5, linestyle='-', label=labels[i])

    ax.set_xlabel("Energy(V)")
    ax.set_ylabel("Charge(A)")
    ax.set_xticks(x2)
    ax.tick_params(axis='x', rotation=0, labelsize=10)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.legend(fontsize='small')
    plt.tight_layout()
    
    return fig

def verify_datasets(datasets):
    return all(
        len(currents) == 7 and all(len(temp) == 10 for temp in currents) and len(y_ticks) == len(y_labels)
        for currents, y_ticks, y_labels in datasets
    )
