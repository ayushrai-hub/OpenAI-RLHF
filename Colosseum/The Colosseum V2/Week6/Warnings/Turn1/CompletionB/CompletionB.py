import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Create fake data with realistic distributions
np.random.seed(42)  # For reproducibility

# Create fake labels with realistic distribution
labels = ['neither', 'fully_supported', 'factual_dispute', 'minor_dispute']
weights = [0.4, 0.3, 0.2, 0.1]  # Realistic distribution
fake_labels = np.random.choice(labels, size=1000, p=weights)
items_new = pd.DataFrame({'golden_label': fake_labels})

# Create realistic precision and recall metrics
precision_neither = 0.85
precision_fully_supported = 0.78
precision_factual_dispute = 0.72
precision_minor_dispute = 0.68

recall_neither = 0.82
recall_fully_supported = 0.75
recall_factual_dispute = 0.70
recall_minor_dispute = 0.65

# Step 1: Determine the count of occurrences for each label
label_counts = items_new['golden_label'].value_counts()

# Step 2: Define precision metrics for each tag
precision_metrics = {
    'neither': precision_neither,
    'fully_supported': precision_fully_supported,
    'factual_dispute': precision_factual_dispute,
    'minor_dispute': precision_minor_dispute
}

# Step 3: Define recall metrics for each tag
recall_metrics = {
    'neither': recall_neither,
    'fully_supported': recall_fully_supported,
    'factual_dispute': recall_factual_dispute,
    'minor_dispute': recall_minor_dispute
}

# Create the visualization
fig, ax1 = plt.subplots(figsize=(10, 6))

# Create bars for the count of occurrences
bars = ax1.bar(label_counts.index, label_counts.values, color='cyan', alpha=0.5)

# Add count values on top of each bar
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, height,
             f'{int(height)}', ha='center', va='bottom')

# Set labels and title for the first y-axis
ax1.set_xlabel('Golden Label', fontweight='bold')
ax1.set_ylabel('Count', fontweight='bold')
ax1.set_title('Count of Entries for Each Golden Label', fontweight='bold', fontsize=16)

# Create second y-axis for precision and recall metrics
ax2 = ax1.twinx()

# Plot precision metrics
for label, precision in precision_metrics.items():
    ax2.plot([label], [precision], marker='o', color='blue')
    ax2.text(label, precision + 0.02, f'P: {precision:.2f}',
             ha='center', va='bottom', color='blue', fontsize=10)

# Plot recall metrics
for label, recall in recall_metrics.items():
    ax2.plot([label], [recall], marker='o', color='green')
    ax2.text(label, recall - 0.05, f'R: {recall:.2f}',
             ha='center', va='top', color='green', fontsize=10)

# Set label for the second y-axis
ax2.set_ylabel('Precision / Recall', fontweight='bold')
ax2.tick_params(axis='y', labelcolor='black')

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Display the plot
plt.show()

# Print the actual counts and metrics for verification
print("\nLabel Counts:")
print(label_counts)
print("\nPrecision Metrics:")
for label, precision in precision_metrics.items():
    print(f"{label}: {precision:.2f}")
print("\nRecall Metrics:")
for label, recall in recall_metrics.items():
    print(f"{label}: {recall:.2f}")