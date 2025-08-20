class Solution:
    def resultsArray(self, nums: list[int], k: int) -> list[int]:
        def po(arr_sum, start):
            expected_sum = k * (2 * start + k - 1) // 2
            return max(nums[start:start + k]) if arr_sum == expected_sum else -1

        current_sum = sum(nums[:k])
        result = []
        for i in range(len(nums) - k + 1):
            start_num = nums[i]
            result.append(po(current_sum, start_num))
            if i + k < len(nums):
                current_sum += nums[i + k] - nums[i]
                
        return result
