import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def create_sample_data(size=100, random_seed=42):
    """
    Create sample dataset with golden labels.
    
    Args:
        size (int): Number of samples to generate
        random_seed (int): Random seed for reproducibility
        
    Returns:
        pd.DataFrame: DataFrame with golden labels
    """
    np.random.seed(random_seed)
    return pd.DataFrame({
        'golden_label': np.random.choice(
            ['neither', 'fully_supported', 'factual_dispute', 'minor_dispute'],
            size=size,
            p=[0.4, 0.3, 0.2, 0.1]
        )
    })

def get_metrics():
    """
    Get sample precision and recall metrics.
    
    Returns:
        tuple: (precision_metrics dict, recall_metrics dict)
    """
    precision_metrics = {
        'neither': 0.85,
        'fully_supported': 0.92,
        'factual_dispute': 0.78,
        'minor_dispute': 0.83
    }
    
    recall_metrics = {
        'neither': 0.88,
        'fully_supported': 0.90,
        'factual_dispute': 0.75,
        'minor_dispute': 0.80
    }
    
    return precision_metrics, recall_metrics

def plot_metrics(items_df, precision_metrics, recall_metrics, figsize=(12, 8)):
    """
    Create visualization of counts, precision, and recall metrics.
    
    Args:
        items_df (pd.DataFrame): DataFrame containing golden labels
        precision_metrics (dict): Dictionary of precision values per label
        recall_metrics (dict): Dictionary of recall values per label
        figsize (tuple): Figure size for the plot
        
    Returns:
        tuple: (figure, (ax1, ax2)) - matplotlib figure and axes objects
    """
    # Calculate label counts
    label_counts = items_df['golden_label'].value_counts()
    
    # Create plot
    fig, ax1 = plt.subplots(figsize=figsize)
    
    # Plot count bars
    bars = ax1.bar(label_counts.index, label_counts.values, color='cyan', alpha=0.5)
    
    # Add count labels
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, height,
                f'{int(height)}', ha='center', va='bottom')
    
    # Set labels and title
    ax1.set_xlabel('Golden Label', fontweight='bold')
    ax1.set_ylabel('Count', fontweight='bold')
    ax1.set_title('Count of Entries for Each Golden Label', fontweight='bold', fontsize=16)
    
    # Create second y-axis for metrics
    ax2 = ax1.twinx()
    
    # Plot precision points and labels
    for label, precision in precision_metrics.items():
        ax2.plot([label], [precision], marker='o', color='blue')
        ax2.text(label, precision, f'Precision: {precision:.2f}',
                ha='center', va='bottom', color='blue')
    
    # Plot recall points and labels
    for label, recall in recall_metrics.items():
        ax2.plot([label], [recall], marker='o', color='green')
        ax2.text(label, recall, f'Recall: {recall:.2f}',
                ha='center', va='bottom', color='green')
    
    # Set y-axis label and range for metrics
    ax2.set_ylabel('Precision & Recall', fontweight='bold')
    ax2.set_ylim(0.5, 1.0)
    
    # Adjust layout
    plt.tight_layout()
    
    return fig, (ax1, ax2)

def main():
    """
    Main function to generate and display the visualization.
    """
    # Create sample data
    items_df = create_sample_data()
    
    # Get metrics
    precision_metrics, recall_metrics = get_metrics()
    
    # Create and show plot
    fig, (ax1, ax2) = plot_metrics(items_df, precision_metrics, recall_metrics)
    plt.show()

if __name__ == "__main__":
    main()