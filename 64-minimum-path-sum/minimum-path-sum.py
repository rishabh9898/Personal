class Solution:
    def minPathSum(self, grid: List[List[int]]) -> int:

        ROW = len(grid)
        COL = len(grid[0])

        for r in range(ROW):
            for c in range(COL):
                if r==0 and c==0:
                    continue
                if r==0 or c==0:
                    if r==0:
                        grid[r][c] += grid[0][c-1]
                    if c==0:
                        grid[r][c] += grid[r-1][0]
                else:
                    grid[r][c] += min(grid[r-1][c],grid[r][c-1])
        
        return grid[-1][-1]