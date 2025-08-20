import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def create_metrics_visualization(label_counts, precision_metrics, recall_metrics, figsize=(10, 6)):
    """
    Create a visualization showing label counts, precision, and recall metrics.
    
    Parameters:
    -----------
    label_counts : pd.Series
        Series containing counts for each label
    precision_metrics : dict
        Dictionary of precision values for each label
    recall_metrics : dict
        Dictionary of recall values for each label
    figsize : tuple
        Size of the figure (width, height)
    
    Returns:
    --------
    tuple
        (fig, ax1, ax2) containing the figure and both axes objects
    """
    # Create figure and primary axis
    fig, ax1 = plt.subplots(figsize=figsize)
    
    # Create bars for label counts
    bars = ax1.bar(label_counts.index, label_counts.values, color='cyan', alpha=0.5)
    
    # Add count labels on bars
    for bar in bars:
        height = float(bar.get_height())
        ax1.text(bar.get_x() + bar.get_width() / 2, height, 
                f"{height:.0f}", ha='center', va='bottom')
    
    # Set primary axis labels
    ax1.set_xlabel('Golden Label', fontweight='bold')
    ax1.set_ylabel('Count', fontweight='bold')
    ax1.set_title('Count of Entries for Each Golden Label', 
                  fontweight='bold', fontsize=16)
    
    # Create secondary axis for metrics
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
                ha='center', va='top', color='green')
    
    # Set secondary axis label
    ax2.set_ylabel('Precision & Recall', fontweight='bold', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    
    return fig, ax1, ax2

def generate_test_data():
    """
    Generate sample data for testing the visualization.
    
    Returns:
    --------
    tuple
        (label_counts, precision_metrics, recall_metrics)
    """
    # Create sample DataFrame
    np.random.seed(42)
    labels = ['neither', 'fully_supported', 'factual_dispute', 'minor_dispute']
    data = pd.DataFrame({
        'golden_label': np.random.choice(labels, size=1000, p=[0.4, 0.3, 0.2, 0.1])
    })
    
    # Calculate label counts
    label_counts = data['golden_label'].value_counts()
    
    # Sample precision and recall metrics
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

def test_visualization():
    """
    Test the visualization function with sample data.
    """
    # Get test data
    label_counts, precision_metrics, recall_metrics = generate_test_data()
    
    # Create visualization
    fig, ax1, ax2 = create_metrics_visualization(label_counts, precision_metrics, recall_metrics)
    
    # Basic tests
    assert len(ax1.patches) == len(label_counts), "Number of bars doesn't match label counts"
    assert len(ax2.lines) == len(precision_metrics) + len(recall_metrics), "Number of points doesn't match metrics"
    
    # Clean up
    plt.close(fig)
    print("Tests passed successfully!")

def main():
    """
    Main function to run the visualization with either real or test data.
    """
    try:
        # Try to use real data if available
        label_counts = items_new['golden_label'].value_counts()
        precision_metrics = {
            'neither': float(precision_neither),
            'fully_supported': float(precision_fully_supported),
            'factual_dispute': float(precision_factual_dispute),
            'minor_dispute': float(precision_minor_dispute)
        }
        recall_metrics = {
            'neither': float(recall_neither),
            'fully_supported': float(recall_fully_supported),
            'factual_dispute': float(recall_factual_dispute),
            'minor_dispute': float(recall_minor_dispute)
        }
    except NameError:
        # Use test data if real data is not available
        print("Using test data since real data is not available")
        label_counts, precision_metrics, recall_metrics = generate_test_data()
    
    # Create and display visualization
    fig, ax1, ax2 = create_metrics_visualization(label_counts, precision_metrics, recall_metrics)
    plt.show()

if __name__ == "__main__":
    # Run tests
    test_visualization()
    
    # Run main visualization
    main()