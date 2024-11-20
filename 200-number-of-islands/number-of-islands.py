class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:

        if not grid:
            return None

        islands = 0

        ROW = len(grid)
        COL = len(grid[0])

        visited = set()

        def dfs(r,c,viisted):
            
            if r not in range(ROW) or c not in range(COL) or (r,c) in visited or grid[r][c]=="0":
                return 
            
            visited.add((r,c))

            dfs(r-1,c,visited)
            dfs(r,c-1,visited)
            dfs(r+1,c,visited)
            dfs(r,c+1,visited)


        for i in range(ROW):
            for j in range(COL):
                if grid[i][j] == "1" and (i,j) not in visited:
                    islands+=1
                    dfs(i,j,visited)
        
        return islands
        