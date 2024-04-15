class Solution:
    def removeOuterParentheses(self, s: str) -> str:

        res = ""
        opened = 0

        for i in s:
            if i == "(" and opened==0:
                opened+=1
            elif i == ")" and opened>=1:
                opened-=1
                if opened == 0:
                    continue
                res+=i
            elif i=="(" and opened>=1:
                res+=i
                opened+=1
        return res
                
            
            
        