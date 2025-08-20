class EvenOccurrenceChecker:
    def __init__(self, array):
        if len(array) == 0:
            raise ValueError("Array cannot be empty")
        self.array = array
        self.n = len(array)
        self.element_to_bit = {}
        self.prefix_masks = [0] * (self.n + 1)
        self._prepprocess_array()
    
    def _prepprocess_array(self):
        bit_position = 0
        for number in self.array:
            if number not in self.element_to_bit:
                self.element_to_bit[number] = bit_position
                bit_position += 1
                if bit_position == 64:
                    raise ValueError("Exceeds 64-bit limitation due to too many distinct elements.")
        for i in range(1, self.n + 1):
            self.prefix_masks[i] = self.prefix_masks[i-1] ^ (1 << self.element_to_bit[self.array[i-1]])
    
    def query_range(self, left, right):
        if (right - left + 1) % 2 != 0:
            raise ValueError("Range length must be even")
        bitmask = self.prefix_masks[right + 1] ^ self.prefix_masks[left]
        return bitmask == 0
