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

# Example usage with two multi-line documents:
document_1 = """Line one of document one
Line two of document one
Line three of document one"""

document_2 = """Line one of document two
Line two of document two
Line three of document two"""

# Calculate WER on entire documents
wer = find_wer(document_1, document_2)
print(f"Word Error Rate (WER) for entire documents: {wer:.2%}")
