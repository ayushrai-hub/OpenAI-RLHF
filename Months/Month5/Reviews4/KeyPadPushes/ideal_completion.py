# ideal_completion.py

from collections import Counter

class Solution:
    def minimumPushes(self, word: str) -> int:

        # Get the frequencies of each letter
        freq = Counter(word)

        # Get the frequencies sorted in descending order
        freqs = sorted(freq.values(), reverse=True)

        # Calculate the total pushes
        total_pushes = sum(f * (i // 8 + 1) for i, f in enumerate(freqs))

        return total_pushes