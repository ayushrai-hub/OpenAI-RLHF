# Plot precision values and connect them to original labels
for label, precision in precision_values.items():
    label_str = str(label)  # Ensure the x position is a scalar-like value
    ax2.plot([label_str], [precision], marker='o', color='b')
    ax2.text(label_str, precision, f'Precision: {precision:.2f}', ha='center', va='bottom', color='b')

# Plot recall values and connect them to original labels
for label, recall in recall_values.items():
    label_str = str(label)  # Ensure correct type for label position
    ax2.plot([label_str], [recall], marker='o', color='g')
    ax2.text(label_str, recall, f'Recall: {recall:.2f}', ha='center', va='bottom', color='g')
