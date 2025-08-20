import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Create fake data
np.random.seed(42)  # For reproducibility

# Create sample DataFrame with fake golden labels
sample_size = 1000
labels = ['neither', 'fully_supported', 'factual_dispute', 'minor_dispute']
items_new = pd.DataFrame({
    'golden_label': np.random.choice(labels, size=sample_size, p=[0.4, 0.3, 0.2, 0.1])
})

# Create fake precision and recall metrics
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

# Step 1: Determine the count of occurrences for each label
label_counts = items_new['golden_label'].value_counts()

# Enlarge the plot size
fig, ax1 = plt.subplots(figsize=(10, 6))

# Create bars for the count of occurrences for each label
bars = ax1.bar(label_counts.index, label_counts.values, color='cyan', alpha=0.5)

# Embed numerical values for the counts of each bar
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width() / 2, height, str(int(height)), ha='center', va='bottom')

# Assign labels and a title
ax1.set_xlabel('Golden Label', fontweight='bold')
ax1.set_ylabel('Count', fontweight='bold')
ax1.set_title('Count of Entries for Each Golden Label', fontweight='bold', fontsize=16)

# Incorporate a second y-axis to illustrate precision and recall metrics
ax2 = ax1.twinx()

# Plot precision metrics and add text labels
for label, precision in precision_metrics.items():
    ax2.plot([label], [precision], marker='o', color='blue')
    ax2.text(label, precision + 0.02, f'P: {precision:.2f}', ha='center', va='bottom', color='blue', fontsize=10)

# Plot recall metrics and add text labels
for label, recall in recall_metrics.items():
    ax2.plot([label], [recall], marker='o', color='green')
    ax2.text(label, recall - 0.05, f'R: {recall:.2f}', ha='center', va='top', color='green', fontsize=10)

# Embed labels for the precision/recall axis
ax2.set_ylabel('Precision / Recall', fontweight='bold')
ax2.tick_params(axis='y', labelcolor='black')

plt.tight_layout()
plt.show()