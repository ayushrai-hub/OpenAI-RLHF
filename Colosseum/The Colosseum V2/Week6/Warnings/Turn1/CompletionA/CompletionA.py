import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Create sample data
np.random.seed(42)
items_new = pd.DataFrame({
    'golden_label': np.random.choice(
        ['neither', 'fully_supported', 'factual_dispute', 'minor_dispute'],
        size=100,
        p=[0.4, 0.3, 0.2, 0.1]
    )
})

# Sample metrics (normally these would be calculated)
precision_neither = 0.85
precision_fully_supported = 0.92
precision_factual_dispute = 0.78
precision_minor_dispute = 0.83

recall_neither = 0.88
recall_fully_supported = 0.90
recall_factual_dispute = 0.75
recall_minor_dispute = 0.80

# Step 1: Determine the count of occurrences
label_counts = items_new['golden_label'].value_counts()

# Step 2: Compute precision metrics for each tag
precision_metrics = {
    'neither': precision_neither,
    'fully_supported': precision_fully_supported,
    'factual_dispute': precision_factual_dispute,
    'minor_dispute': precision_minor_dispute
}

# Step 3: Calculate recall metrics for each tag
recall_metrics = {
    'neither': recall_neither,
    'fully_supported': recall_fully_supported,
    'factual_dispute': recall_factual_dispute,
    'minor_dispute': recall_minor_dispute
}

# Enlarge the plot size
fig, ax1 = plt.subplots(figsize=(12, 8))  # Made slightly larger to accommodate labels

# Create bars for the count of occurrences for each label
bars = ax1.bar(label_counts.index, label_counts.values, color='cyan', alpha=0.5)

# Embed numerical values for the counts of each bar
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width() / 2, height, 
             f'{int(height)}', ha='center', va='bottom')

# Assign labels and a title
ax1.set_xlabel('Golden Label', fontweight='bold')
ax1.set_ylabel('Count', fontweight='bold')
ax1.set_title('Count of Entries for Each Golden Label', fontweight='bold', fontsize=16)

# Incorporate a second y-axis
ax2 = ax1.twinx()

# Modified snippet:
for label, precision in precision_metrics.items():
    ax2.plot([label], [precision], marker='o', color='blue')
    ax2.text(str(label), precision, f'Precision: {precision:.2f}', ha='center', va='bottom', color='blue')

for label, recall in recall_metrics.items():
    ax2.plot([label], [recall], marker='o', color='green')
    ax2.text(str(label), recall, f'Recall: {recall:.2f}', ha='center', va='bottom', color='green')


# Set y-axis label and range
ax2.set_ylabel('Precision & Recall', fontweight='bold')
ax2.set_ylim(0.5, 1.0)  # Adjust based on your actual metrics range

# Adjust layout to prevent label cutoff
plt.tight_layout()

plt.show()