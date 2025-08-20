import numpy as np

# Function to compute Word Error Rate (WER)
def find_wer(reference, hypothesis):
    r = reference.split()
    h = hypothesis.split()
    d = np.zeros((len(r)+1, len(h)+1))

    for i in range(len(r)+1):
        d[i][0] = i
    for j in range(len(h)+1):
        d[0][j] = j

    for i in range(1, len(r)+1):
        for j in range(1, len(h)+1):
        if r[i-1] == h[j-1]:
            d[i][j] = d[i-1][j-1]
        else:
            d[i][j] = 1 + min(d[i-1][j],    # Deletion
                              d[i][j-1],    # Insertion
                              d[i-1][j-1])  # Substitution

    wer = d[len(r)][len(h)] / len(r) if len(r) > 0 else float('inf')
    return wer

# Read documents
with open('document1.txt', 'r') as file:
    text_doc1 = file.read()

with open('document2.txt', 'r') as file:
    text_doc2 = file.read()

# Remove any leading/trailing whitespace and concatenate lines
text_doc1 = ' '.join(text_doc1.strip().split())
text_doc2 = ' '.join(text_doc2.strip().split())

# Compute WER over the entire text
wer = find_wer(text_doc1, text_doc2)
print(f"Overall WER between the two documents: {wer*100:.2f}%")
