class Solution:
    def pacificAtlantic(self, heights: List[List[int]]) -> List[List[int]]:

        ROW,COL = len(heights),len(heights[0])

        pac = set()
        atl = set()

        def dfs(r,c,prev,visited):

            if r<0 or r>=ROW or c<0 or c>=COL or (r,c) in visited or prev>heights[r][c]:
                return 
            
            visited.add((r,c))
            dfs(r-1,c,heights[r][c],visited)
            dfs(r,c-1,heights[r][c],visited)
            dfs(r+1,c,heights[r][c],visited)
            dfs(r,c+1,heights[r][c],visited)


        #  pacific ocean
        for c in range(COL):
            dfs(0,c,heights[0][c],pac)
            dfs(ROW-1,c,heights[ROW-1][c],atl)
        
        # atl ocean
        for r in range(ROW):
            dfs(r,0,heights[r][0],pac)
            dfs(r,COL-1,heights[r][COL-1],atl)

        res = []
        for (i,j) in pac:
            if (i,j) in atl:
                res.append([i,j])

        return res


        
        

        