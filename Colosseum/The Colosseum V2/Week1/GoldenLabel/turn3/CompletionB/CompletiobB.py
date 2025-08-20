import matplotlib.pyplot as plt

# Step 1: Determine the count of occurrences for each label in the `golden_label` column
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
fig, ax1 = plt.subplots(figsize=(10, 6))  # Customize width and height as necessary

# Create bars for the count of occurrences for each label
bars = ax1.bar(label_counts.index, label_counts.values, color='cyan', alpha=0.5)

# Embed numerical values for the counts of each bar
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width() / 2, height, str(height), ha='center', va='bottom')

# Assign labels and a title
ax1.set_xlabel('Golden Label', fontweight='bold')  # Apply bold font weight
ax1.set_ylabel('Count', fontweight='bold')  # Apply bold font weight
ax1.set_title('Count of Entries for Each Golden Label', fontweight='bold', fontsize=16)  # Apply bold font weight and increase font size

# Incorporate a second y-axis to illustrate precision metrics
ax2 = ax1.twinx()

# Connect precision metrics to initial labels and plot them
for label, precision in precision_metrics.items():
    ax2.plot([label], [precision], marker='o', color='blue')
    # Ensure label and precision values are scalars
    ax2.text(str(label), float(precision), f'Precision: {precision:.2f}', ha='center', va='bottom', color='blue')

# Connect recall metrics to initial labels and plot them
for label, recall in recall_metrics.items():
    ax2.plot([label], [recall], marker='o', color='green')
    # Ensure label and recall values are scalars
    ax2.text(str(label), float(recall), f'Recall: {recall:.2f}', ha='center', va='bottom', color='green')

# Embed labels for the precision axis
ax2.set_ylabel('Precision & Recall', fontweight='bold', color='blue')  # Apply bold font weight
ax2.tick_params(axis='y', labelcolor='blue')  # Assign color to y-axis labels

plt.show()
