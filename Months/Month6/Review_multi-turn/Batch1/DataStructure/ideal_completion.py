from typing import List

class EvenOccurrenceChecker:
    def __init__(self, array: List[int]) -> None:
        if not array:
            raise ValueError("Array must not be empty.")
        self.array = array
        self._preprocess_array()
    
    def _preprocess_array(self) -> None:
        self.bitmask = [0] * (len(self.array) + 1)
        element_to_bit = {}
        current_bit = 0
        
        for i, num in enumerate(self.array):
            if num not in element_to_bit:
                if current_bit >= 64:
                    raise ValueError("Exceeded maximum of 64 unique elements.")
                element_to_bit[num] = 1 << current_bit
                current_bit += 1
            self.bitmask[i + 1] = self.bitmask[i] ^ element_to_bit[num]
    
    def query_range(self, left: int, right: int) -> bool:
        if not (0 <= left <= right < len(self.array)):
            raise ValueError("Invalid range indices.")
        if (right - left + 1) % 2 != 0:
            raise ValueError("Range length must be even.")
        return self.bitmask[right + 1] ^ self.bitmask[left] == 0
