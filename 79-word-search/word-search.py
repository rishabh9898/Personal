class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:

        if not board:
            return None

        ROW = len(board)
        COL = len(board[0])

        visited = set()

        res = ""

        def dfs(r,c,visited,idx):

            if r not in range(ROW) or c not in range(COL) or (r,c) in visited or board[r][c] !=word[idx]:
                return False

            if idx+1 == len(word):
                return True 

            visited.add((r,c))
            idx+=1
            if (dfs(r-1,c,visited,idx) or
                dfs(r,c-1,visited,idx) or
                dfs(r+1,c,visited,idx) or 
                dfs(r,c+1,visited,idx)):
                return True
            

            #  need to come back to original letter if not found from one branch
            visited.remove((r,c))
        

        for r in range(ROW):
            for c in range(COL):
                idx = 0
                if board[r][c] == word[0]:
                    if dfs(r,c,visited,idx):
                        return True
                    
        return False




        