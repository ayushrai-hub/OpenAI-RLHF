import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Tuple, List
import numpy as np

def calculate_label_counts(df: pd.DataFrame, label_column: str = 'golden_label') -> pd.Series:
    """
    Calculate the count of occurrences for each label.
    
    Args:
        df (pd.DataFrame): Input DataFrame containing the labels
        label_column (str): Name of the column containing labels
        
    Returns:
        pd.Series: Count of occurrences for each label
        
    Raises:
        ValueError: If label_column is not found in DataFrame
    """
    if label_column not in df.columns:
        raise ValueError(f"Column '{label_column}' not found in DataFrame")
    
    return df[label_column].value_counts()

def create_metrics_plot(
    label_counts: pd.Series,
    precision_metrics: Dict[str, float],
    recall_metrics: Dict[str, float],
    figsize: Tuple[int, int] = (10, 6)
) -> Tuple[plt.Figure, plt.Axes, plt.Axes]:
    """
    Create a plot showing label counts, precision, and recall metrics.
    
    Args:
        label_counts (pd.Series): Count of occurrences for each label
        precision_metrics (Dict[str, float]): Precision values for each label
        recall_metrics (Dict[str, float]): Recall values for each label
        figsize (Tuple[int, int]): Size of the figure (width, height)
        
    Returns:
        Tuple[plt.Figure, plt.Axes, plt.Axes]: Figure and both axes objects
        
    Raises:
        ValueError: If metrics dictionaries don't match label_counts indices
    """
    # Validate inputs
    labels = label_counts.index
    if not all(label in precision_metrics for label in labels):
        raise ValueError("Precision metrics missing for some labels")
    if not all(label in recall_metrics for label in labels):
        raise ValueError("Recall metrics missing for some labels")

    # Create plot
    fig, ax1 = plt.subplots(figsize=figsize)
    ax2 = ax1.twinx()
    
    # Plot bars
    bars = ax1.bar(labels, label_counts.values, color='cyan', alpha=0.5)
    
    # Add value labels to bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            str(int(height)),
            ha='center',
            va='bottom'
        )
    
    # Plot precision and recall points
    for label in labels:
        # Precision points
        ax2.plot(
            [label],
            [precision_metrics[label]],
            marker='o',
            color='blue',
            label='Precision' if label == labels[0] else ""
        )
        ax2.text(
            label,
            precision_metrics[label] + 0.02,
            f'P: {precision_metrics[label]:.2f}',
            ha='center',
            va='bottom',
            color='blue',
            fontsize=10
        )
        
        # Recall points
        ax2.plot(
            [label],
            [recall_metrics[label]],
            marker='o',
            color='green',
            label='Recall' if label == labels[0] else ""
        )
        ax2.text(
            label,
            recall_metrics[label] - 0.05,
            f'R: {recall_metrics[label]:.2f}',
            ha='center',
            va='top',
            color='green',
            fontsize=10
        )
    
    # Set labels and styling
    ax1.set_xlabel('Golden Label', fontweight='bold')
    ax1.set_ylabel('Count', fontweight='bold')
    ax2.set_ylabel('Precision / Recall', fontweight='bold')
    ax1.set_title('Count of Entries for Each Golden Label', fontweight='bold', fontsize=16)
    ax2.tick_params(axis='y', labelcolor='black')
    
    return fig, ax1, ax2

def plot_metrics(
    df: pd.DataFrame,
    precision_metrics: Dict[str, float],
    recall_metrics: Dict[str, float],
    label_column: str = 'golden_label',
    figsize: Tuple[int, int] = (10, 6)
) -> Tuple[plt.Figure, plt.Axes, plt.Axes]:
    """
    Main function to create the metrics visualization.
    
    Args:
        df (pd.DataFrame): Input DataFrame containing the labels
        precision_metrics (Dict[str, float]): Precision values for each label
        recall_metrics (Dict[str, float]): Recall values for each label
        label_column (str): Name of the column containing labels
        figsize (Tuple[int, int]): Size of the figure
        
    Returns:
        Tuple[plt.Figure, plt.Axes, plt.Axes]: Figure and both axes objects
    """
    label_counts = calculate_label_counts(df, label_column)
    return create_metrics_plot(label_counts, precision_metrics, recall_metrics, figsize)

# Example usage:
if __name__ == "__main__":
    # Sample data
    data = {
        'golden_label': ['neither', 'fully_supported', 'factual_dispute', 'minor_dispute'] * 25
    }
    df = pd.DataFrame(data)
    
    # Sample metrics
    precision_metrics = {
        'neither': 0.85,
        'fully_supported': 0.78,
        'factual_dispute': 0.92,
        'minor_dispute': 0.88
    }
    
    recall_metrics = {
        'neither': 0.82,
        'fully_supported': 0.75,
        'factual_dispute': 0.89,
        'minor_dispute': 0.86
    }
    
    # Create plot
    fig, ax1, ax2 = plot_metrics(df, precision_metrics, recall_metrics)
    plt.show()

def test_calculate_label_counts():
    """Unit test for calculate_label_counts function"""
    data = pd.DataFrame({
        'golden_label': ['A', 'B', 'A', 'C']
    })
    counts = calculate_label_counts(data)
    assert counts['A'] == 2
    assert counts['B'] == 1
    assert counts['C'] == 1
    
    # Test error handling
    try:
        calculate_label_counts(data, 'nonexistent_column')
        assert False, "Should have raised ValueError"
    except ValueError:
        pass