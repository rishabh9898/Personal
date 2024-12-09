class Solution:
    def myAtoi(self, s: str) -> int:

        counter = 0
        res = ""
        sign = 1
        visited = 0

        while counter<len(s):
            
            if (s[counter] == " ")  and visited == 0:
                counter+=1
                continue
            elif s[counter] == "0" and visited == 0:
                counter+=1
                visited = 1
                continue

            elif s[counter] == "+" and visited == 0:
                counter+=1
                visited = 1
                continue

            elif s[counter] == "-" and visited == 0:
                sign = -1*sign
                counter+=1
                visited = 1
                continue

            elif s[counter].isdigit():
                visited = 1
                res+=s[counter]
                counter+=1
            
            else:
                break

        if not res:
            return 0
        
        return max(min(sign*int(res),2**31-1),-2**31)



            


        

