import matplotlib.pyplot as plt
import numpy as np

def generate_plot_data():
    x2 = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    z1 = np.array([0.4, 0.5, 0.7, 1, 1.2, 1.4, 1.5, 2, 2.2, 2.4])
    z2 = np.array([0.4, 0.7, 1, 1.3, 1.5, 1.7, 1.8, 2.3, 2.7, 3])
    z3 = np.array([0.7, 1, 1.2, 1.5, 1.7, 1.9, 2.2, 2.7, 3, 3.3])
    z4 = np.array([0.7, 1.1, 1.3, 1.6, 1.9, 2.2, 2.5, 3, 3.5, 3.9])
    z5 = np.array([0.9, 1.2, 1.4, 1.7, 2.2, 2.5, 3, 3.5, 4, 4.5])
    z6 = np.array([0.9, 1.3, 1.6, 2, 2.6, 3.2, 3.8, 4.5, 5, 5.8])
    z7 = np.array([0.9, 1.4, 1.9, 2.5, 3.2, 4, 4.8, 5.5, 6.2, 6.9])
    z_ticks = np.array([1, 2, 3, 4, 5, 6, 7, 8])
    
    return x2, z1, z2, z3, z4, z5, z6, z7, z_ticks

def create_energy_charge_plot(x2, z1, z2, z3, z4, z5, z6, z7, z_ticks):
    plt.figure(figsize=(10, 6))
    plt.plot(x2, z1, marker='s', markersize=5, linestyle='-', label="(40$^\circ$C)")
    plt.plot(x2, z2, marker='o', markersize=5, linestyle='-', label="(60$^\circ$C)")
    plt.plot(x2, z3, marker='<', markersize=5, linestyle='-', label="(120$^\circ$C)")
    plt.plot(x2, z4, marker='>', markersize=5, linestyle='-', label="(140$^\circ$C)")
    plt.plot(x2, z5, marker='v', markersize=5, linestyle='-', label="(100$^\circ$C)")
    plt.plot(x2, z6, marker='^', markersize=5, linestyle='-', label="(80$^\circ$C)")
    plt.plot(x2, z7, marker='D', markersize=5, linestyle='-', label="(160$^\circ$C)")
    
    plt.xlabel('Energy (V)')
    plt.ylabel('Charge (A)')
    plt.yticks(z_ticks, [f'{val}.0$\\times$10$^{{-10}}$' for val in z_ticks])
    plt.legend(fontsize='small')
    plt.tight_layout()
    
    return plt.gcf()

if __name__ == "__main__":
    x2, z1, z2, z3, z4, z5, z6, z7, z_ticks = generate_plot_data()
    fig = create_energy_charge_plot(x2, z1, z2, z3, z4, z5, z6, z7, z_ticks)
    plt.show()