import matplotlib.pyplot as plt
import os

# Define output directory
output_dir = '/kaggle/working/compare'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Function to generate plots
def generate_plots(epochs, data, title, ylabel, output_filename):
    plt.figure(figsize=(14, 7))
    for label, values in data.items():
        plt.plot(epochs[label], values, label=label, marker='o')
    plt.title(title)
    plt.xlabel('Epochs')
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, output_filename), quality=100, dpi=300)
    plt.close()

# Example usage (data should be passed as parameters to generate_plots in a unit test)
# generate_plots(epochs_alexnet, {'Improved AlexNet': training_loss_alexnet}, 'Training Loss Comparison', 'Training Loss', 'training_loss_comparison.jpeg')
