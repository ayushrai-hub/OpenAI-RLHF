import matplotlib.pyplot as plt

# Step 1: Calculate count of entries for each value in the golden_label column
label_counts = items_new['golden_label']..value_counts()

# Ensure label indexes are lists to avoid uncertainties in indexing.
labels_index_list = label_counts.index.tolist()

# Step 2: Calculate precision values for each label
precision_values = {
    'neither': precision_neither,
    'supported_fully': precision_supported_fully,
    'contradiction_factual': precision_contradiction_factual,
    'contradiction_minor': precision_contradiction_minor
}

# Step 3: Calculate recall values for each label
recall_values = {
    'neither': recall_neither,
    'supported_fully': recall_supported_fully,
    'contradiction_factual': recall_contradiction_factual,
    'contradiction_minor': recall_contradiction_minor
}

# Increase the size of the plot
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot the counts of entries for each label as bars
bars = ax1.bar(labels_index_list, label_counts.values, color='pink', alpha=0.5)

# Add numeric values for count of entries for each bar
for bar in bars:
    height = bar.get_height()
    label_at_bar = labels_index_list[bars.index(bar)] # Access label for corresponding bar
    ax1.text(bar.get_x() + bar.get_width() / 2, height, str(height), ha='center', va='bottom')

# Add labels and title
ax1.set_xlabel('Golden Label', fontweight='bold')
ax1.set_ylabel('Count', fontweight='bold')
ax1.set_title('Count of Entries for Each Golden Label', fontweight='bold', fontsize=16)

# Add a second y-axis for precision and recall values
ax2 = ax1.twinx()

# Plot precision values and connect them to original labels
for label, precision in precision_values.items():
    ax2.plot(label, precision, marker='o', color='b')
    ax2.text(label, precision, f'Precision: {precision:.2f}', ha='center', va='bottom', color='b')

# Plot recall values and connect them to original labels
for label, recall in recall_values.items():
    ax2.plot(label, recall, marker='o', color='g')
    ax2.text(label, recall, f'Recall: {recall:.2f}', ha='center', va='bottom', color='g')

# Add labels for precision axis
ax2.set_ylabel('Precision & Recall', fontweight='bold', color='b')
ax2.tick_params(axis='y', labelcolor='b')

plt.show()
