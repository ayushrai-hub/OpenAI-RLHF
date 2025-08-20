if i < len(nums) - 1 and not jump_points:
    return False

jump_points = 0  # Initialize to zero
for i, num in enumerate(nums):
    if i > jump_points:
        return False
    jump_points = max(jump_points, i + num)
