import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def calculate_metrics(items_df):
    """
    Calculate label counts, precision, and recall metrics from the dataframe.
    
    Args:
        items_df (pd.DataFrame): DataFrame containing 'golden_label' column
        
    Returns:
        tuple: (label_counts, precision_metrics, recall_metrics)
    """
    # Calculate label counts
    label_counts = items_df['golden_label'].value_counts()
    
    # Calculate metrics for each label
    labels = ['neither', 'fully_supported', 'factual_dispute', 'minor_dispute']
    precision_metrics = {label: items_df[f'precision_{label}'].iloc[0] for label in labels}
    recall_metrics = {label: items_df[f'recall_{label}'].iloc[0] for label in labels}
    
    return label_counts, precision_metrics, recall_metrics

def create_metrics_plot(label_counts, precision_metrics, recall_metrics, figsize=(10, 6)):
    """
    Create a plot showing label counts, precision, and recall metrics.
    
    Args:
        label_counts (pd.Series): Counts of each label
        precision_metrics (dict): Precision values for each label
        recall_metrics (dict): Recall values for each label
        figsize (tuple): Figure size (width, height)
        
    Returns:
        tuple: (fig, ax1, ax2) - Figure and axis objects for testing
    """
    fig, ax1 = plt.subplots(figsize=figsize)
    
    # Create bars
    bars = ax1.bar(label_counts.index, label_counts.values, color='cyan', alpha=0.5)
    
    # Add count labels
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, height, 
                str(int(height)), ha='center', va='bottom')
    
    # Set labels and title
    ax1.set_xlabel('Golden Label', fontweight='bold')
    ax1.set_ylabel('Count', fontweight='bold')
    ax1.set_title('Count of Entries for Each Golden Label', 
                  fontweight='bold', fontsize=16)
    
    # Create second y-axis
    ax2 = ax1.twinx()
    
    # Plot metrics
    for label in precision_metrics:
        # Plot precision
        ax2.plot([label], [precision_metrics[label]], 
                 marker='o', color='blue')
        ax2.text(label, precision_metrics[label], 
                f'Precision: {precision_metrics[label]:.2f}', 
                ha='center', va='bottom', color='blue')
        
        # Plot recall
        ax2.plot([label], [recall_metrics[label]], 
                 marker='o', color='green')
        ax2.text(label, recall_metrics[label], 
                f'Recall: {recall_metrics[label]:.2f}', 
                ha='center', va='bottom', color='green')
    
    ax2.set_ylabel('Precision & Recall', fontweight='bold', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    
    return fig, ax1, ax2

# Test functions
def test_calculate_metrics():
    """Test the calculate_metrics function with sample data"""
    # Create sample data
    sample_data = pd.DataFrame({
        'golden_label': ['neither', 'fully_supported', 'neither'],
        'precision_neither': [0.8] * 3,
        'precision_fully_supported': [0.7] * 3,
        'precision_factual_dispute': [0.6] * 3,
        'precision_minor_dispute': [0.5] * 3,
        'recall_neither': [0.75] * 3,
        'recall_fully_supported': [0.65] * 3,
        'recall_factual_dispute': [0.55] * 3,
        'recall_minor_dispute': [0.45] * 3
    })
    
    label_counts, precision_metrics, recall_metrics = calculate_metrics(sample_data)
    
    # Test assertions
    assert len(label_counts) > 0, "Label counts should not be empty"
    assert len(precision_metrics) == 4, "Should have 4 precision metrics"
    assert len(recall_metrics) == 4, "Should have 4 recall metrics"
    assert label_counts['neither'] == 2, "Should have 2 'neither' labels"
    assert precision_metrics['neither'] == 0.8, "Incorrect precision value"
    assert recall_metrics['neither'] == 0.75, "Incorrect recall value"

def test_create_metrics_plot():
    """Test the plot creation with sample data"""
    # Create sample data
    label_counts = pd.Series({'neither': 2, 'fully_supported': 1})
    precision_metrics = {
        'neither': 0.8,
        'fully_supported': 0.7,
        'factual_dispute': 0.6,
        'minor_dispute': 0.5
    }
    recall_metrics = {
        'neither': 0.75,
        'fully_supported': 0.65,
        'factual_dispute': 0.55,
        'minor_dispute': 0.45
    }
    
    # Create plot
    fig, ax1, ax2 = create_metrics_plot(label_counts, precision_metrics, recall_metrics)
    
    # Test assertions
    assert len(ax1.patches) == len(label_counts), "Should have correct number of bars"
    assert len(ax2.lines) == len(precision_metrics) * 2, "Should have correct number of metric points"
    
    plt.close(fig)  # Clean up

if __name__ == "__main__":
    # Run tests
    test_calculate_metrics()
    test_create_metrics_plot()
    print("All tests passed!")