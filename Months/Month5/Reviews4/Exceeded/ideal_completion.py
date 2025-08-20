# ideal_completion.py
class Solution:
    def resultsArray(self, nums: list[int], k: int) -> list[int]:
        def po(arr):
            # Instead of sorting, check if the array is consecutive and sorted
            for i in range(1, len(arr)):
                if arr[i] != arr[i-1] + 1:
                    return -1
            return arr[-1]
        return [po(nums[i:i+k]) for i in range(len(nums) - k + 1)]