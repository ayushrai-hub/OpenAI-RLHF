import matplotlib.pyplot as plt

# Step 1: Calculate count of entries for each value in the golden_label column
label_counts = items_new['golden_label'].value_counts()

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
fig, ax1 = plt.subplots(figsize=(10, 6))  # Adjust width and height as needed

# Plot the counts of entries for each label as bars
bars = ax1.bar(label_counts.index, label_counts.values, color='pink', alpha=0.5)

# Add numeric values for count of entries for each bar
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width() / 2, height, str(height), ha='center', va='bottom')

# Add labels and title
ax1.set_xlabel('Golden Label', fontweight='bold')  # Set font weight to bold
ax1.set_ylabel('Count', fontweight='bold')  # Set font weight to bold
ax1.set_title('Count of Entries for Each Golden Label', fontweight='bold', fontsize=16)  # Set font weight to bold and increase font size

# Add a second y-axis for precision and recall values
ax2 = ax1.twinx()

# Plot precision values and connect them to original labels
for label, precision in precision_values.items():
    precision_value = precision if isinstance(precision, (int, float)) else precision.item()
    ax2.plot([label], [precision_value], marker='o', color='b')
    ax2.text(label, precision_value, f'Precision: {precision_value:.2f}', ha='center', va='bottom', color='b')

# Plot recall values and connect them to original labels
for label, recall in recall_values.items():
    recall_value = recall if isinstance(recall, (int, float)) else recall.item()
    ax2.plot([label], [recall_value], marker='o', color='g')
    ax2.text(label, recall_value, f'Recall: {recall_value:.2f}', ha='center', va='bottom', color='g')

# Add labels for precision axis
ax2.set_ylabel('Precision & Recall', fontweight='bold', color='b')  # Set font weight to bold
ax2.tick_params(axis='y', labelcolor='b')  # Set color for y-axis labels

plt.show()
