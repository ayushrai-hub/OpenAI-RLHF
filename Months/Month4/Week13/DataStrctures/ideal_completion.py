class EvenOccurrenceChecker:
    def __init__(self, array):
        """Initialize checker with input array"""
        if not array:
            raise ValueError("Array cannot be empty")
        
        self.array = array
        self.n = len(array)
        self.element_to_bit = {}
        self.prefix_masks = [0] * (self.n + 1)
        self._preprocess_array()

    def _preprocess_array(self):
        """Build prefix XOR masks for efficient range queries"""
        # Map unique elements to bit positions
        bit_pos = 0
        for num in self.array:
            if num not in self.element_to_bit:
                if bit_pos >= 64:  # Using 64-bit integers
                    raise ValueError("Too many unique elements (>64)")
                self.element_to_bit[num] = bit_pos
                bit_pos += 1
        
        # Construct prefix XOR masks
        for i in range(1, self.n + 1):
            curr_element = self.array[i-1]
            bit_mask = 1 << self.element_to_bit[curr_element]
            self.prefix_masks[i] = self.prefix_masks[i-1] ^ bit_mask

    def query_range(self, left, right):
        """Check if all elements in range [left, right] occur even times"""
        # Validate input range
        if not (0 <= left <= right < self.n):
            raise ValueError("Invalid range")
        if (right - left + 1) % 2:  # Length must be even
            raise ValueError("Range length must be even")
            
        # XOR of prefix masks gives frequency parity
        range_mask = self.prefix_masks[right + 1] ^ self.prefix_masks[left]
        return range_mask == 0

# Usage example:
nums = [1, 2, 1, 2, 3, 3, 4, 4]
checker = EvenOccurrenceChecker(nums)

# Test cases
test_ranges = [
    (0, 3),  # [1,2,1,2] - all even occurrences
    (2, 5),  # [1,2,3,3] - Some odd occurrences
    (1, 4)   # [2,1,2,3] - Some odd occurrences
]

for l, r in test_ranges:
    result = checker.query_range(l, r)
    print(f"Range [{l},{r}]: {'All even occurrences' if result else 'Some odd occurrences'}")