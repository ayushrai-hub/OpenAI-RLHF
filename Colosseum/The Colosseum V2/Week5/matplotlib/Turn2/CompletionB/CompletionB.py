import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Create sample data
data = {
    'golden_label': ['neither'] * 50 + ['fully_supported'] * 30 + 
                    ['factual_dispute'] * 20 + ['minor_dispute'] * 15
}
items_new = pd.DataFrame(data)

# Step 1: Determine the count of occurrences for each label
label_counts = items_new['golden_label'].value_counts()

# Sample precision and recall metrics (you can replace these with your actual values)
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

# Enlarge the plot size
fig, ax1 = plt.subplots(figsize=(10, 6))

# Create bars for the count of occurrences for each label
bars = ax1.bar(label_counts.index, label_counts.values, color='cyan', alpha=0.5)

# Embed numerical values for the counts of each bar
for bar in bars:
    height = float(bar.get_height())
    ax1.text(bar.get_x() + bar.get_width() / 2, height, f"{height:.0f}", 
             ha='center', va='bottom')

# Assign labels and a title
ax1.set_xlabel('Golden Label', fontweight='bold')
ax1.set_ylabel('Count', fontweight='bold')
ax1.set_title('Count of Entries for Each Golden Label', fontweight='bold', fontsize=16)

# Incorporate a second y-axis to illustrate precision metrics
ax2 = ax1.twinx()

# Connect precision metrics to initial labels and plot them
for label, precision in precision_metrics.items():
    ax2.plot([label], [precision], marker='o', color='blue')
    ax2.text(label, precision, f'Precision: {precision:.2f}', 
             ha='center', va='bottom', color='blue')

# Connect recall metrics to initial labels and plot them
for label, recall in recall_metrics.items():
    ax2.plot([label], [recall], marker='o', color='green')
    ax2.text(label, recall, f'Recall: {recall:.2f}', 
             ha='center', va='top', color='green')

# Embed labels for the precision axis
ax2.set_ylabel('Precision & Recall', fontweight='bold', color='blue')
ax2.tick_params(axis='y', labelcolor='blue')

# Adjust layout to prevent label overlap
plt.tight_layout()

plt.show()