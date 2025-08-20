from typing import List

class Solution:
    def pacificAtlantic(self, heights: List[List[int]]) -> List[List[int]]:
        if not heights or not heights[0]:
            return []
        
        m, n = len(heights), len(heights[0])

        pacific = set()
        atlantic = set()

        def flood(row, col, ocean):
            if (row, col) in ocean:
                return
            ocean.add((row, col))
            directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            for dr, dc in directions:
                nr, nc = row + dr, col + dc
                if 0 <= nr < m and 0 <= nc < n and heights[nr][nc] >= heights[row][col]:
                    flood(nr, nc, ocean)

        # Start from the Pacific Ocean (left and top edges)
        for row in range(m):
            flood(row, 0, pacific)     # Left edge
            flood(row, n - 1, atlantic) # Right edge
        for col in range(n):
            flood(0, col, pacific)     # Top edge
            flood(m - 1, col, atlantic) # Bottom edge

        # Find all cells that can reach both oceans
        result = [(r, c) for r in range(m) for c in range(n) if (r, c) in pacific and (r, c) in atlantic]

        return result
