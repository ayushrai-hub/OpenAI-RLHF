import numpy as np

def find_wer(reference, hypothesis):
    # Break the texts into individual words
    r = reference.split()
    h = hypothesis.split()

    # Construct a matrix for edit distances (Levenshtein distance)
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
                                  d[i-1][j-1]) # Substitution

    wer = d[len(r)][len(h)] / len(r) if len(r) > 0 else 0
    return wer

document_1_lines = [
    "We like it or not once my pals and I land, we are officially deserted here for the next seven days",
    "That was probably the most terrifying thing I've ever experienced",
    "First things first we must get very far from the point we rappelled down"
]

document_2_lines = [
    "We like it or not as soon as my friends and I touch the ground, we are officially stranded here for the next seven days",
    "That might have been the scariest thing I've ever done",
    "First things first we gotta get really far away from where we were held down"
]

# Ensure both documents have the same number of lines (if not, handle accordingly)
num_lines = min(len(document_1_lines), len(document_2_lines))

line_wer_results = []
for i in range(num_lines):
    line_1 = document_1_lines[i]
    line_2 = document_2_lines[i]
    wer = find_wer(line_1, line_2)
    line_wer_results.append((i, wer))

for line_index, wer in line_wer_results:
    print(f"Line {line_index+1} WER: {wer:.2%}")
