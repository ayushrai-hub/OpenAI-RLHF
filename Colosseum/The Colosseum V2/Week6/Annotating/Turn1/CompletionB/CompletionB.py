import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Create sample data
np.random.seed(42)
categories = ['neither', 'fully_supported', 'factual_dispute', 'minor_dispute']
data = np.random.choice(categories, size=1000, p=[0.4, 0.3, 0.2, 0.1])
items_new = pd.DataFrame({'golden_label': data})

# Create sample metrics
precision_neither = 0.85
precision_fully_supported = 0.75
precision_factual_dispute = 0.60
precision_minor_dispute = 0.50

recall_neither = 0.90
recall_fully_supported = 0.80
recall_factual_dispute = 0.65
recall_minor_dispute = 0.55

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

# Connect precision metrics to initial labels and plot them
for label, precision in precision_metrics.items():
    ax2.plot([label], [precision], marker='o', color='blue')
    ax2.text(label, precision, f'Precision: {precision:.2f}', ha='center', va='bottom', color='blue')

# Connect recall metrics to initial labels and plot them
for label, recall in recall_metrics.items():
    ax2.plot([label], [recall], marker='o', color='green')
    ax2.text(label, recall, f'Recall: {recall:.2f}', ha='center', va='bottom', color='green')

# Embed labels for the precision axis
ax2.set_ylabel('Precision & Recall', fontweight='bold')

# Add a small legend to clarify P and R
ax2.plot([], [], 'o', color='blue', label='Precision (P)')
ax2.plot([], [], 'o', color='green', label='Recall (R)')
ax2.legend(loc='upper right')

# Adjust layout to make room for text
plt.tight_layout()
plt.show()