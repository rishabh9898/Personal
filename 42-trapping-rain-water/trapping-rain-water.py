class Solution:
    def trap(self, height: List[int]) -> int:

        if len(height)<2:
            return 0
        L = [0]*len(height)
        R = [0]*len(height)

        trapped = 0

        L[0] = height[0]

        for i in range(1,len(height)):
            L[i] = max(height[i],L[i-1])

        R[len(height)-1] = height[len(height)-1]

        for i in range(len(height)-2,-1,-1):
            R[i] = max(height[i],R[i+1])

        for i in range(len(height)):
            if(min(L[i],R[i]) - height[i]) <0:
                continue
            else:
                trapped += min(R[i],L[i]) - height[i]

        return trapped


        