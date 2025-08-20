import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def generate_sample_data(n_samples=1000):
    """
    Generate sample data for testing the visualization.
    
    Returns:
    --------
    tuple
        (label_counts, precision_metrics, recall_metrics)
    """
    # Create sample labels
    labels = ['neither', 'fully_supported', 'factual_dispute', 'minor_dispute']
    
    # Generate random data
    np.random.seed(42)  # For reproducibility
    data = pd.DataFrame({
        'golden_label': np.random.choice(labels, size=n_samples, p=[0.4, 0.3, 0.2, 0.1])
    })
    
    # Calculate label counts
    label_counts = data['golden_label'].value_counts()
    
    # Generate sample metrics
    precision_metrics = {
        'neither': 0.85,
        'fully_supported': 0.78,
        'factual_dispute': 0.72,
        'minor_dispute': 0.68
    }
    
    recall_metrics = {
        'neither': 0.82,
        'fully_supported': 0.75,
        'factual_dispute': 0.70,
        'minor_dispute': 0.65
    }
    
    return label_counts, precision_metrics, recall_metrics

def create_metrics_plot(label_counts, precision_metrics, recall_metrics, figsize=(10, 6)):
    """
    Create a plot showing counts, precision, and recall metrics for labels.
    
    Parameters:
    -----------
    label_counts : pd.Series
        Counts of occurrences for each label
    precision_metrics : dict
        Dictionary mapping labels to precision values
    recall_metrics : dict
        Dictionary mapping labels to recall values
    figsize : tuple
        Figure size in inches (width, height)
        
    Returns:
    --------
    tuple
        Figure and axes objects (fig, ax1, ax2)
    """
    # Convert any numpy values to python scalars to avoid deprecation warnings
    label_counts = {str(k): float(v) for k, v in label_counts.items()}
    precision_metrics = {str(k): float(v) for k, v in precision_metrics.items()}
    recall_metrics = {str(k): float(v) for k, v in recall_metrics.items()}
    
    # Create plot
    fig, ax1 = plt.subplots(figsize=figsize)
    
    # Plot count bars
    bars = ax1.bar(label_counts.keys(), label_counts.values(), color='cyan', alpha=0.5)
    
    # Add count labels
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, height, 
                f'{height:.0f}', ha='center', va='bottom')
    
    # Set primary axis labels
    ax1.set_xlabel('Golden Label', fontweight='bold')
    ax1.set_ylabel('Count', fontweight='bold')
    ax1.set_title('Count of Entries for Each Golden Label', 
                  fontweight='bold', fontsize=16)
    
    # Create secondary axis for metrics
    ax2 = ax1.twinx()
    
    # Plot precision metrics and annotate them correctly
    for label, precision in precision_metrics.items():
        precision_val = float(precision)  # Convert to scalar
        ax2.plot([label], [precision_val], marker='o', color='blue')
        ax2.text(label, precision_val, f'Precision: {precision_val:.2f}', 
                ha='center', va='bottom', color='blue')

    # Plot recall metrics and annotate them correctly
    for label, recall in recall_metrics.items():
        recall_val = float(recall)  # Convert to scalars
        ax2.plot([label], [recall_val], marker='o', color='green')
        ax2.text(label, recall_val, f'Recall: {recall_val:.2f}', 
                ha='center', va='bottom', color='green')

    # Set secondary axis label
    ax2.set_ylabel('Precision & Recall', fontweight='bold', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    
    return fig, ax1, ax2

def main():
    # Generate sample data
    label_counts, precision_metrics, recall_metrics = generate_sample_data()
    
    # Create plot
    fig, ax1, ax2 = create_metrics_plot(label_counts, precision_metrics, recall_metrics)
    plt.show()

if __name__ == "__main__":
    main()