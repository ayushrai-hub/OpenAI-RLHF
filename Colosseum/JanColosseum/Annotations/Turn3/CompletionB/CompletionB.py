# Ensure labels are converted to strings
for label, precision in precision_values.items():
    ax2.plot([str(label)], [precision], marker='o', color='b')  # Ensure label is string
    ax2.text(str(label), precision, f'Precision: {precision:.2f}', ha='center', va='bottom', color='b')  # Ensure label is string

for label, recall in recall_values.items():
    ax2.plot([str(label)], [recall], marker='o', color='g')  # Ensure label is string
    ax2.text(str(label), recall, f'Recall: {recall:.2f}', ha='center', va='bottom', color='g')  # Ensure label is string
