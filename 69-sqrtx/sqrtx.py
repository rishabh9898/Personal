class Solution:
    def mySqrt(self, x: int) -> int:

        num = 1

        for i in range(1,2**31):
            if i*i == x:
                num = i
                return num
            elif i*i>x:
                num = i-1
                return num
        return
        
        