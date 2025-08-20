class Solution:
    def minimumPushes(self, word: str) -> int:
        from collections import Counter
        frequency = Counter(word)
        freq_list = sorted(frequency.items(), key=lambda x: -x[1])

        total_pushes = 0
        key_presses = 1
        for _, freq in freq_list:
            total_pushes += freq * key_presses
            key_presses += 1

        return total_pushes
