import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Step 0: Create sample data for testing
# Create a sample dataframe with golden labels
data = {
    'golden_label': ['neither', 'fully_supported', 'factual_dispute', 'minor_dispute',
                     'neither', 'fully_supported', 'factual_dispute', 'minor_dispute',
                     'neither', 'fully_supported', 'factual_dispute', 'minor_dispute',
                     'neither', 'neither', 'fully_supported', 'fully_supported',
                     'factual_dispute', 'minor_dispute', 'minor_dispute', 'fully_supported']
}

items_new = pd.DataFrame(data)

# Define sample precision and recall values for testing
precision_neither = 0.85
precision_fully_supported = 0.92
precision_factual_dispute = 0.78
precision_minor_dispute = 0.70

recall_neither = 0.90
recall_fully_supported = 0.88
recall_factual_dispute = 0.75
recall_minor_dispute = 0.82

# Step 1: Determine the count of occurrences for each label in the `golden_label` column
label_counts = items_new['golden_label'].value_counts()

# Step 2: Compute precision metrics for each tag
precision_metrics = {
    'neither': float(precision_neither),
    'fully_supported': float(precision_fully_supported),
    'factual_dispute': float(precision_factual_dispute),
    'minor_dispute': float(precision_minor_dispute)
}

# Step 3: Calculate recall metrics for each tag
recall_metrics = {
    'neither': float(recall_neither),
    'fully_supported': float(recall_fully_supported),
    'factual_dispute': float(recall_factual_dispute),
    'minor_dispute': float(recall_minor_dispute)
}

# Enlarge the plot size
fig, ax1 = plt.subplots(figsize=(10, 6))

# Create bars for the count of occurrences for each label
bars = ax1.bar(label_counts.index, label_counts.values, color='cyan', alpha=0.5)

# Embed numerical values for the counts of each bar
for bar in bars:
    height = float(bar.get_height())  # Convert to float
    ax1.text(bar.get_x() + bar.get_width() / 2, height, f"{height:.0f}", ha='center', va='bottom')

# Assign labels and a title
ax1.set_xlabel('Golden Label', fontweight='bold')
ax1.set_ylabel('Count', fontweight='bold')
ax1.set_title('Count of Entries for Each Golden Label', fontweight='bold', fontsize=16)

# Incorporate a second y-axis to illustrate precision metrics
ax2 = ax1.twinx()

# Set y-range for precision and recall axis (0 to 1 range)
ax2.set_ylim([0, 1.1])  # Adding 0.1 for text space

# Sort labels to match the order in label_counts.index
sorted_labels = list(label_counts.index)

# Connect precision metrics to sorted labels and plot them
x_positions = range(len(sorted_labels))
precision_values = [precision_metrics[label] for label in sorted_labels]
recall_values = [recall_metrics[label] for label in sorted_labels]

# Plot precision points and lines
ax2.plot(sorted_labels, precision_values, marker='o', color='blue', label='Precision')
for i, (label, precision) in enumerate(zip(sorted_labels, precision_values)):
    ax2.text(i, precision + 0.02, f'{precision:.2f}', ha='center', va='bottom', color='blue')

# Plot recall points and lines
ax2.plot(sorted_labels, recall_values, marker='s', color='green', label='Recall')
for i, (label, recall) in enumerate(zip(sorted_labels, recall_values)):
    ax2.text(i, recall - 0.05, f'{recall:.2f}', ha='center', va='top', color='green')

# Embed labels for the precision/recall axis
ax2.set_ylabel('Precision & Recall', fontweight='bold', color='blue')
ax2.tick_params(axis='y', labelcolor='blue')

# Add legend
ax2.legend(loc='upper right')

# Adjust layout to prevent clipping of labels
plt.tight_layout()

# Display the plot
plt.savefig('golden_label_visualization.png')  # Save to file
plt.show()  # Show interactively