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
    lines_doc1 = file.readlines()

with open('document2.txt', 'r') as file:
    lines_doc2 = file.readlines()

# Ensure both documents have the same number of lines
if len(lines_doc1) != len(lines_doc2):
    raise ValueError("Documents have different numbers of lines.")

line_wers = []
for i, (ref_line, hyp_line) in enumerate(zip(lines_doc1, lines_doc2)):
    wer = find_wer(ref_line.strip(), hyp_line.strip())
    line_wers.append(wer)
    print(f"Line {i+1} WER: {wer*100:.2f}%")

# Calculate average WER
average_wer = sum(line_wers) / len(line_wers)
print(f"\nAverage WER across all lines: {average_wer*100:.2f}%")
